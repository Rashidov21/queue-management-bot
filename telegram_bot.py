#!/usr/bin/env python3
"""
Telegram Bot for Queue Management System
Integrates with Django REST API
"""

import asyncio
import logging
import os
import sys
from datetime import date, time, timedelta
from typing import Dict, List

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


# Command handlers
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Start command handler"""
    await state.clear()
    
    user = await get_or_create_user(message.from_user.id, message.from_user.username or "user")
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 View Services"), KeyboardButton(text="📅 My Bookings")],
            [KeyboardButton(text="👤 Profile"), KeyboardButton(text="ℹ️ Help")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    await message.answer(
        f"👋 Hello {message.from_user.first_name}!\n\n"
        f"Welcome to the Queue Management Bot! 🚀\n\n"
        f"Choose an option from the menu below:",
        reply_markup=keyboard
    )


@dp.message(lambda message: message.text == "📋 View Services")
async def show_services(message: types.Message, state: FSMContext):
    """Show available services"""
    services_data = await make_api_request('GET', '/services/')
    
    if 'error' in services_data:
        await message.answer("❌ Sorry, I couldn't fetch services right now. Please try again later.")
        return
    
    services = services_data.get('results', [])
    
    if not services:
        await message.answer("📋 No services available at the moment.")
        return
    
    keyboard = []
    for service in services:
        keyboard.append([InlineKeyboardButton(
            text=f"{service['name']} ({service['duration_minutes']} min)",
            callback_data=f"service_{service['id']}"
        )])
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await message.answer(
        "📋 Available Services:\n\n" + 
        "\n".join([f"• {s['name']} - {s['duration_minutes']} minutes" for s in services]),
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
        await callback_query.message.edit_text("❌ Sorry, couldn't fetch providers. Please try again.")
        return
    
    providers = providers_data.get('results', [])
    
    if not providers:
        await callback_query.message.edit_text("❌ No providers available for this service.")
        return
    
    keyboard = []
    for provider in providers:
        keyboard.append([InlineKeyboardButton(
            text=f"{provider['user_name']} - {provider['service_name']}",
            callback_data=f"provider_{provider['id']}"
        )])
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback_query.message.edit_text(
        f"👨‍💼 Choose a provider:\n\n" +
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
        await callback_query.message.edit_text("❌ Provider not found.")
        return
    
    working_days = ", ".join([day.capitalize() for day in provider_data['working_days']])
    
    keyboard = [
        [InlineKeyboardButton(text="Today", callback_data="date_today")],
        [InlineKeyboardButton(text="Tomorrow", callback_data="date_tomorrow")],
        [InlineKeyboardButton(text="Day After Tomorrow", callback_data="date_day_after")]
    ]
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback_query.message.edit_text(
        f"📅 Choose a date for your booking:\n\n"
        f"Provider: {provider_data['user_name']}\n"
        f"Service: {provider_data['service_name']}\n"
        f"Working days: {working_days}\n"
        f"Hours: {provider_data['start_time']} - {provider_data['end_time']}",
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
        await callback_query.message.edit_text("❌ Invalid date selection.")
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
        await callback_query.message.edit_text("❌ Couldn't fetch available time slots.")
        return
    
    slots = slots_data if isinstance(slots_data, list) else []
    
    if not slots:
        await callback_query.message.edit_text("❌ No available time slots for this date.")
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
        f"🕐 Available time slots for {selected_date}:\n\n"
        f"Choose a time slot:",
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
        [InlineKeyboardButton(text="✅ Confirm Booking", callback_data="confirm_booking")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_booking")]
    ]
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback_query.message.edit_text(
        f"📋 Please confirm your booking:\n\n"
        f"Date: {data['date']}\n"
        f"Time: {time_str}\n\n"
        f"Do you want to confirm this booking?",
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
        f"✅ Booking confirmed!\n\n"
        f"Date: {data['date']}\n"
        f"Time: {data['time']}\n\n"
        f"You will receive a reminder before your appointment.\n\n"
        f"Use /start to return to the main menu."
    )
    
    await state.clear()


@dp.callback_query(lambda c: c.data == "cancel_booking")
async def cancel_booking(callback_query: types.CallbackQuery, state: FSMContext):
    """Cancel booking process"""
    await callback_query.message.edit_text(
        "❌ Booking cancelled.\n\nUse /start to return to the main menu."
    )
    await state.clear()


@dp.message(lambda message: message.text == "📅 My Bookings")
async def show_my_bookings(message: types.Message):
    """Show user's bookings"""
    # For MVP, show a placeholder
    await message.answer(
        "📅 Your Bookings:\n\n"
        "No bookings found.\n\n"
        "Use 'View Services' to make a new booking!"
    )


@dp.message(lambda message: message.text == "👤 Profile")
async def show_profile(message: types.Message):
    """Show user profile"""
    await message.answer(
        f"👤 Your Profile:\n\n"
        f"Name: {message.from_user.first_name} {message.from_user.last_name or ''}\n"
        f"Username: @{message.from_user.username or 'Not set'}\n"
        f"Telegram ID: {message.from_user.id}\n"
        f"Role: Client\n\n"
        f"Use /start to return to the main menu."
    )


@dp.message(lambda message: message.text == "ℹ️ Help")
async def show_help(message: types.Message):
    """Show help information"""
    await message.answer(
        "ℹ️ Help & Information:\n\n"
        "🤖 This bot helps you book services with providers.\n\n"
        "📋 **Available Commands:**\n"
        "• /start - Main menu\n"
        "• View Services - Browse available services\n"
        "• My Bookings - View your bookings\n"
        "• Profile - View your profile\n"
        "• Help - Show this help\n\n"
        "📞 **Support:**\n"
        "If you need help, contact the administrator.\n\n"
        "Use /start to return to the main menu."
    )


@dp.message()
async def handle_unknown_message(message: types.Message):
    """Handle unknown messages"""
    await message.answer(
        "❓ I don't understand that command.\n\n"
        "Use /start to see the main menu or /help for assistance."
    )


async def main():
    """Main function to start the bot"""
    logger.info("Starting Telegram bot...")
    
    # Delete webhook if it exists
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        sys.exit(1)
