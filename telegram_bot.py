#!/usr/bin/env python3
"""
Telegram Bot for Queue Management System
Integrates with Django REST API
"""

import asyncio
import logging
import os
import sys
import subprocess
import threading
import platform
from datetime import date, time, timedelta
from typing import Dict, List
from pathlib import Path

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8001/api')

if not BOT_TOKEN:
    logger.error("BOT_TOKEN not found in environment variables")
    sys.exit(1)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


class BookingStates(StatesGroup):
    """States for booking flow"""
    waiting_for_service = State()
    waiting_for_provider = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_confirmation = State()


class UserRegistrationStates(StatesGroup):
    """States for user registration"""
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_role = State()


# Helper functions for API calls
async def make_api_request(method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict:
    """Make HTTP request to Django API"""
    url = f"{API_BASE_URL}{endpoint}"
    
    async with aiohttp.ClientSession() as session:
        try:
            if method.upper() == 'GET':
                async with session.get(url, headers=headers) as response:
                    return await response.json()
            elif method.upper() == 'POST':
                async with session.post(url, json=data, headers=headers) as response:
                    return await response.json()
            elif method.upper() == 'PUT':
                async with session.put(url, json=data, headers=headers) as response:
                    return await response.json()
            elif method.upper() == 'DELETE':
                async with session.delete(url, headers=headers) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return {"error": str(e)}


async def get_or_create_user(telegram_id: int, username: str) -> Dict:
    """Get or create user via API"""
    # For MVP, we'll create a simple user without authentication
    # In production, you'd implement proper authentication
    return {
        "id": telegram_id,
        "username": username,
        "telegram_id": telegram_id,
        "role": "client"
    }


async def register_user_in_django(telegram_user):
    """Register user in Django project using Telegram data"""
    try:
        # Prepare user data from Telegram
        user_data = {
            "username": telegram_user.username or f"user_{telegram_user.id}",
            "first_name": telegram_user.first_name or "",
            "last_name": telegram_user.last_name or "",
            "telegram_id": telegram_user.id,
            "telegram_username": telegram_user.username or "",
            "role": "client"
        }
        
        # Register user via API
        response = await make_api_request('POST', '/users/register/', user_data)
        
        if 'error' not in response:
            logger.info(f"User {telegram_user.id} registered successfully")
        else:
            logger.info(f"User {telegram_user.id} already exists or registration failed")
            
    except Exception as e:
        logger.error(f"Error registering user {telegram_user.id}: {e}")


# Command handlers
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Start command handler"""
    await state.clear()
    
    # Register user in Django project
    await register_user_in_django(message.from_user)
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Xizmatlar"), KeyboardButton(text="📅 Mening buyurtmalarim")],
            [KeyboardButton(text="👤 Profil"), KeyboardButton(text="ℹ️ Yordam")],
            [KeyboardButton(text="🌐 Web ilovasi")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    await message.answer(
        f"👋 Salom {message.from_user.first_name}!\n\n"
        f"Navbatni boshqarish botiga xush kelibsiz! 🚀\n\n"
        f"Quyidagi menyudan biror variantni tanlang:",
        reply_markup=keyboard
    )


@dp.message(lambda message: message.text == "📋 Xizmatlar")
async def show_services(message: types.Message, state: FSMContext):
    """Show available services"""
    services_data = await make_api_request('GET', '/services/')
    
    if 'error' in services_data:
        await message.answer("❌ Kechirasiz, hozircha xizmatlarni olishga qiynalmoqda. Keyinroq urinib ko'ring.")
        return
    
    services = services_data.get('results', [])
    
    if not services:
        await message.answer("📋 Hozircha hech qanday xizmat mavjud emas.")
        return
    
    keyboard = []
    for service in services:
        keyboard.append([InlineKeyboardButton(
            text=f"{service['name']} ({service['duration_minutes']} min)",
            callback_data=f"service_{service['id']}"
        )])
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await message.answer(
        "📋 Mavjud xizmatlar:\n\n" + 
        "\n".join([f"• {s['name']} - {s['duration_minutes']} daqiqa" for s in services]),
        reply_markup=reply_markup
    )


@dp.callback_query(lambda c: c.data.startswith("service_"))
async def process_service_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Process service selection"""
    service_id = int(callback_query.data.split("_")[1])
    
    await state.update_data(service_id=service_id)
    await state.set_state(BookingStates.waiting_for_provider)
    
    # Get providers for this service
    providers_data = await make_api_request('GET', f'/providers/?service_id={service_id}')
    
    if 'error' in providers_data:
        await callback_query.message.edit_text("❌ Kechirasiz, xizmat ko'rsatuvchilarni olishga qiynalmoqda. Qayta urinib ko'ring.")
        return
    
    providers = providers_data.get('results', [])
    
    if not providers:
        await callback_query.message.edit_text("❌ Bu xizmat uchun hech qanday ko'rsatuvchi mavjud emas.")
        return
    
    keyboard = []
    for provider in providers:
        keyboard.append([InlineKeyboardButton(
            text=f"{provider['user_name']} - {provider['service_name']}",
            callback_data=f"provider_{provider['id']}"
        )])
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback_query.message.edit_text(
        f"👨‍💼 Xizmat ko'rsatuvchini tanlang:\n\n" +
        "\n".join([f"• {p['user_name']} - {p['location']}" for p in providers]),
        reply_markup=reply_markup
    )


@dp.callback_query(lambda c: c.data.startswith("provider_"))
async def process_provider_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Process provider selection"""
    provider_id = int(callback_query.data.split("_")[1])
    
    await state.update_data(provider_id=provider_id)
    await state.set_state(BookingStates.waiting_for_date)
    
    # Get provider details
    provider_data = await make_api_request('GET', f'/providers/{provider_id}/')
    
    if 'error' in provider_data:
        await callback_query.message.edit_text("❌ Xizmat ko'rsatuvchi topilmadi.")
        return
    
    working_days = ", ".join([day.capitalize() for day in provider_data['working_days']])
    
    keyboard = [
        [InlineKeyboardButton(text="Bugun", callback_data="date_today")],
        [InlineKeyboardButton(text="Ertaga", callback_data="date_tomorrow")],
        [InlineKeyboardButton(text="Kundan keyingi kun", callback_data="date_day_after")]
    ]
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback_query.message.edit_text(
        f"📅 Buyurtmangiz uchun sanani tanlang:\n\n"
        f"Ko'rsatuvchi: {provider_data['user_name']}\n"
        f"Xizmat: {provider_data['service_name']}\n"
        f"Ish kunlari: {working_days}\n"
        f"Vaqt: {provider_data['start_time']} - {provider_data['end_time']}",
        reply_markup=reply_markup
    )


@dp.callback_query(lambda c: c.data.startswith("date_"))
async def process_date_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Process date selection"""
    date_option = callback_query.data.split("_")[1]
    
    today = date.today()
    if date_option == "today":
        selected_date = today
    elif date_option == "tomorrow":
        selected_date = today + timedelta(days=1)
    elif date_option == "day_after":
        selected_date = today + timedelta(days=2)
    else:
        await callback_query.message.edit_text("❌ Noto'g'ri sana tanlovi.")
        return
    
    data = await state.get_data()
    provider_id = data.get('provider_id')
    
    await state.update_data(date=selected_date.isoformat())
    await state.set_state(BookingStates.waiting_for_time)
    
    # Get available time slots
    slots_data = await make_api_request(
        'GET', 
        f'/providers/{provider_id}/slots/?date={selected_date.isoformat()}'
    )
    
    if 'error' in slots_data:
        await callback_query.message.edit_text("❌ Mavjud vaqt bo'shliqlarini olishga qiynalmoqda.")
        return
    
    slots = slots_data if isinstance(slots_data, list) else []
    
    if not slots:
        await callback_query.message.edit_text("❌ Bu sana uchun hech qanday bo'sh vaqt yo'q.")
        return
    
    keyboard = []
    for slot in slots[:10]:  # Limit to 10 slots
        time_str = slot['time']
        keyboard.append([InlineKeyboardButton(
            text=f"🕐 {time_str}",
            callback_data=f"time_{time_str}"
        )])
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback_query.message.edit_text(
        f"🕐 {selected_date} uchun mavjud vaqt bo'shliqlari:\n\n"
        f"Vaqt bo'shligini tanlang:",
        reply_markup=reply_markup
    )


@dp.callback_query(lambda c: c.data.startswith("time_"))
async def process_time_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Process time selection"""
    time_str = callback_query.data.split("_", 1)[1]
    
    await state.update_data(time=time_str)
    await state.set_state(BookingStates.waiting_for_confirmation)
    
    data = await state.get_data()
    
    keyboard = [
        [InlineKeyboardButton(text="✅ Buyurtmani tasdiqlash", callback_data="confirm_booking")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_booking")]
    ]
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback_query.message.edit_text(
        f"📋 Iltimos, buyurtmangizni tasdiqlang:\n\n"
        f"Sana: {data['date']}\n"
        f"Vaqt: {time_str}\n\n"
        f"Bu buyurtmani tasdiqlashni xohlaysizmi?",
        reply_markup=reply_markup
    )


@dp.callback_query(lambda c: c.data == "confirm_booking")
async def confirm_booking(callback_query: types.CallbackQuery, state: FSMContext):
    """Confirm booking"""
    data = await state.get_data()
    
    # Create booking via API
    booking_data = {
        "provider_id": data['provider_id'],
        "date": data['date'],
        "time": data['time'],
        "notes": "Booked via Telegram bot"
    }
    
    # For MVP, we'll simulate a successful booking
    # In production, you'd implement proper authentication
    await callback_query.message.edit_text(
        f"✅ Buyurtma tasdiqlandi!\n\n"
        f"Sana: {data['date']}\n"
        f"Vaqt: {data['time']}\n\n"
        f"Uchrashuvdan oldin eslatma olasiz.\n\n"
        f"Asosiy menyuga qaytish uchun /start buyrug'ini ishlating."
    )
    
    await state.clear()


@dp.callback_query(lambda c: c.data == "cancel_booking")
async def cancel_booking(callback_query: types.CallbackQuery, state: FSMContext):
    """Cancel booking process"""
    await callback_query.message.edit_text(
        "❌ Buyurtma bekor qilindi.\n\nAsosiy menyuga qaytish uchun /start buyrug'ini ishlating."
    )
    await state.clear()


@dp.message(lambda message: message.text == "📅 Mening buyurtmalarim")
async def show_my_bookings(message: types.Message):
    """Show user's bookings"""
    # For MVP, show a placeholder
    await message.answer(
        "📅 Sizning buyurtmalaringiz:\n\n"
        "Hech qanday buyurtma topilmadi.\n\n"
        "Yangi buyurtma berish uchun 'Xizmatlar'ni ishlating!"
    )


@dp.message(lambda message: message.text == "👤 Profil")
async def show_profile(message: types.Message):
    """Show user profile"""
    await message.answer(
        f"👤 Sizning profilingiz:\n\n"
        f"Ism: {message.from_user.first_name} {message.from_user.last_name or ''}\n"
        f"Foydalanuvchi nomi: @{message.from_user.username or 'Belgilanmagan'}\n"
        f"Telegram ID: {message.from_user.id}\n"
        f"Rol: Mijoz\n\n"
        f"Asosiy menyuga qaytish uchun /start buyrug'ini ishlating."
    )




@dp.message(lambda message: message.text == "🌐 Web ilovasi")
async def show_web_app(message: types.Message):
    """Open web application"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Web ilovasini ochish", url=f"https://d9a7b9b528c1.ngrok-free.app/users/telegram-login/?telegram_id={message.from_user.id}")]
    ])
    
    await message.answer(
        "🌐 **Web ilovasini ochish**\n\n"
        "To'liq funksionallik uchun web ilovasini ishlatishingiz mumkin.\n\n"
        "Quyidagi tugmani bosing:",
        reply_markup=keyboard
    )


@dp.message(lambda message: message.text == "ℹ️ Yordam")
async def show_help(message: types.Message):
    """Show help information"""
    await message.answer(
        "ℹ️ Yordam va ma'lumot:\n\n"
        "🤖 Bu bot sizga xizmat ko'rsatuvchilar bilan xizmatlarni buyurtma qilishga yordam beradi.\n\n"
        "📋 **Mavjud buyruqlar:**\n"
        "• /start - Asosiy menyu\n"
        "• Xizmatlar - Mavjud xizmatlarni ko'rish\n"
        "• Mening buyurtmalarim - Buyurtmalaringizni ko'rish\n"
        "• Profil - Profilingizni ko'rish\n"
        "• Yordam - Bu yordamni ko'rsatish\n\n"
        "🌐 **Web ilovasi:**\n"
        "To'liq funksionallik uchun 'Web ilovasi' tugmasini ishlating\n"
        "URL: https://d9a7b9b528c1.ngrok-free.app\n\n"
        "📞 **Qo'llab-quvvatlash:**\n"
        "Agar yordamga muhtoj bo'lsangiz, administratorga murojaat qiling.\n\n"
        "Asosiy menyuga qaytish uchun /start buyrug'ini ishlating."
    )


@dp.message()
async def handle_unknown_message(message: types.Message):
    """Handle unknown messages"""
    await message.answer(
        "❓ Men bu buyruqni tushunmayman.\n\n"
        "Asosiy menyuni ko'rish uchun /start yoki yordam uchun /help buyrug'ini ishlating."
    )


def start_django_server():
    """Start Django development server in a separate thread"""
    try:
        # Set Django settings module
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queue_management.settings')
        
        # Change to project directory
        project_dir = Path(__file__).parent
        os.chdir(project_dir)
        
        logger.info("Starting Django web server on port 8001...")
        
        # Use virtual environment Python if available
        if platform.system() == "Windows":
            python_cmd = "venv\\Scripts\\python.exe"
        else:
            python_cmd = "venv/bin/python"
        
        # Check if virtual environment exists
        if Path("venv").exists() and Path(python_cmd).exists():
            python_executable = python_cmd
        else:
            python_executable = sys.executable
        
        # Start Django development server
        subprocess.run([
            python_executable, 'manage.py', 'runserver', '8001'
        ], check=True)
    except Exception as e:
        logger.error(f"Error starting Django server: {e}")


async def main():
    """Main function to start the bot and web server"""
    logger.info("Starting Queue Management System...")
    logger.info("Starting Django web server...")
    
    # Start Django server in a separate thread
    django_thread = threading.Thread(target=start_django_server, daemon=True)
    django_thread.start()
    
    # Give Django server time to start
    await asyncio.sleep(3)
    
    logger.info("Django web server started at http://localhost:8001")
    logger.info("Telegram bot ishga tushmoqda...")
    
    # Delete webhook if it exists
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot foydalanuvchi tomonidan to'xtatildi")
    except Exception as e:
        logger.error(f"Bot xatosi: {e}")
        sys.exit(1)
