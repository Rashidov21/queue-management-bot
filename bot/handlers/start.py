from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import User
from database.db import get_db
from bot.states.user_states import RoleSelection, ProviderRegistration, ClientBooking
from bot.keyboards.main import get_main_menu_keyboard, get_services_keyboard, get_provider_menu_keyboard, get_client_menu_keyboard
from bot.utils.helpers import get_today_str

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    await state.clear()
    
    # Check if user already exists
    async with get_db() as db:
        result = await db.execute(select(User).where(User.telegram_id == message.from_user.id))
        user = result.scalar_one_or_none()
    
    if user:
        # User exists, show appropriate menu
        if user.role == "provider":
            await message.answer(
                f"👋 Welcome back, {user.full_name}!\n\n"
                "You're logged in as a Service Provider. How can I help you today?",
                reply_markup=get_provider_menu_keyboard()
            )
        else:
            await message.answer(
                f"👋 Welcome back, {user.full_name}!\n\n"
                "You're logged in as a Client. How can I help you today?",
                reply_markup=get_client_menu_keyboard()
            )
    else:
        # New user, show role selection
        await message.answer(
            "👋 Welcome! Please choose who you are:",
            reply_markup=get_main_menu_keyboard()
        )
        await state.set_state(RoleSelection.waiting_for_role)


@router.message(F.text == "💇‍♂️ I'm a Service Provider")
async def select_provider_role(message: Message, state: FSMContext):
    """Handle provider role selection"""
    await state.set_state(ProviderRegistration.waiting_for_name)
    await message.answer(
        "💼 Great! Let's set up your provider profile.\n\n"
        "Please enter your full name:",
        reply_markup=None
    )


@router.message(F.text == "🙋‍♀️ I'm a Client")
async def select_client_role(message: Message, state: FSMContext):
    """Handle client role selection"""
    await message.answer(
        "🙋‍♀️ Welcome! Let's find you a service.\n\n"
        "Please select a service you want to book:"
    )
    await state.set_state(ClientBooking.waiting_for_service)
    await show_services_menu(message)


async def show_services_menu(message: Message):
    """Show available services menu"""
    from database.models import Service
    
    async with get_db() as db:
        result = await db.execute(select(Service))
        services = result.scalars().all()
    
    if not services:
        await message.answer(
            "😔 Sorry, no services are available at the moment.\n"
            "Please try again later or contact support."
        )
        return
    
    keyboard = get_services_keyboard(services)
    await message.answer("🔧 Choose a service:", reply_markup=keyboard)


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    """Show main menu"""
    await state.clear()
    
    async with get_db() as db:
        result = await db.execute(select(User).where(User.telegram_id == message.from_user.id))
        user = result.scalar_one_or_none()
    
    if not user:
        await message.answer(
            "👋 Welcome! Please choose who you are:",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    if user.role == "provider":
        await message.answer(
            f"👋 Welcome back, {user.full_name}!\n\n"
            "You're logged in as a Service Provider. How can I help you today?",
            reply_markup=get_provider_menu_keyboard()
        )
    else:
        await message.answer(
            f"👋 Welcome back, {user.full_name}!\n\n"
            "You're logged in as a Client. How can I help you today?",
            reply_markup=get_client_menu_keyboard()
        )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Show help information"""
    help_text = """
🤖 **Queue Management Bot Help**

**For Service Providers:**
• 📋 My Bookings - View and manage your appointments
• 📅 Manage Schedule - Set your working hours and days
• ⚙️ Settings - Update your profile and availability
• 📊 Dashboard - View your booking statistics

**For Clients:**
• 🔍 Book Service - Browse and book available services
• 📋 My Bookings - View and manage your appointments
• ℹ️ Help - Show this help message

**Commands:**
• /start - Start the bot or return to main menu
• /menu - Show main menu
• /help - Show this help message

Need more help? Contact support! 😊
"""
    await message.answer(help_text, parse_mode="Markdown")


@router.message(F.text == "🔙 Back")
async def handle_back(message: Message, state: FSMContext):
    """Handle back button"""
    await cmd_menu(message, state)


@router.message(F.text == "❌ Cancel")
async def handle_cancel(message: Message, state: FSMContext):
    """Handle cancel button"""
    await state.clear()
    await cmd_menu(message, state)
