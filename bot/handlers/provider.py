from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, time

from database.models import User, Provider, Service, Booking, Slot
from database.db import get_db
from bot.states.user_states import ProviderRegistration, ProviderSchedule
from bot.keyboards.main import (
    get_services_keyboard, get_working_days_keyboard, get_provider_menu_keyboard,
    get_availability_toggle_keyboard, get_back_keyboard, get_cancel_keyboard
)
from bot.utils.helpers import (
    format_time, parse_time, is_valid_time_format, generate_time_slots,
    get_weekday_name, get_emoji_for_status, format_date, get_today_str
)

router = Router()


@router.message(ProviderRegistration.waiting_for_name)
async def process_provider_name(message: Message, state: FSMContext):
    """Process provider name input"""
    if len(message.text) < 2:
        await message.answer("❌ Please enter a valid name (at least 2 characters).")
        return
    
    await state.update_data(full_name=message.text)
    
    # Show services selection
    async with get_db() as db:
        result = await db.execute(select(Service))
        services = result.scalars().all()
    
    if not services:
        await message.answer(
            "😔 No services available. Please contact admin to add services.",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    keyboard = get_services_keyboard(services)
    await message.answer("🔧 Select your service:", reply_markup=keyboard)
    await state.set_state(ProviderRegistration.waiting_for_service)


@router.callback_query(F.data.startswith("service_"))
async def process_service_selection(callback: CallbackQuery, state: FSMContext):
    """Process service selection for provider registration"""
    service_id = int(callback.data.split("_")[1])
    await state.update_data(service_id=service_id)
    
    await callback.message.edit_text(
        "📍 Please enter your location or service description:\n\n"
        "Example: 'Downtown Salon, Main Street 123' or 'Home visits in Central District'"
    )
    await callback.answer()
    await state.set_state(ProviderRegistration.waiting_for_location)


@router.message(ProviderRegistration.waiting_for_location)
async def process_location(message: Message, state: FSMContext):
    """Process location input"""
    await state.update_data(location=message.text)
    
    await message.answer(
        "📞 Please enter your phone number (optional):\n\n"
        "Example: +1234567890 or leave empty to skip",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(ProviderRegistration.waiting_for_phone)


@router.message(ProviderRegistration.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """Process phone input"""
    phone = message.text if message.text != "🔙 Back" else None
    await state.update_data(phone=phone)
    
    await message.answer(
        "📅 Select your working days:\n\n"
        "Click on the days you work, then click '✅ Done'",
        reply_markup=get_working_days_keyboard()
    )
    await state.set_state(ProviderRegistration.waiting_for_working_days)


@router.callback_query(F.data.startswith("day_"))
async def toggle_working_day(callback: CallbackQuery, state: FSMContext):
    """Toggle working day selection"""
    day_number = int(callback.data.split("_")[1])
    
    data = await state.get_data()
    working_days = data.get("working_days", [])
    
    if day_number in working_days:
        working_days.remove(day_number)
    else:
        working_days.append(day_number)
    
    await state.update_data(working_days=working_days)
    
    # Update keyboard to show selected days
    keyboard = get_working_days_keyboard()
    selected_days = [get_weekday_name(d) for d in working_days]
    status_text = f"Selected: {', '.join(selected_days)}" if selected_days else "No days selected"
    
    await callback.message.edit_text(
        f"📅 Select your working days:\n\n"
        f"Current selection: {status_text}\n\n"
        f"Click on the days you work, then click '✅ Done'",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "days_done")
async def process_working_days(callback: CallbackQuery, state: FSMContext):
    """Process working days selection"""
    data = await state.get_data()
    working_days = data.get("working_days", [])
    
    if not working_days:
        await callback.message.edit_text(
            "❌ Please select at least one working day.",
            reply_markup=get_working_days_keyboard()
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        "⏰ Enter your working hours start time (HH:MM format):\n\n"
        "Example: 09:00"
    )
    await callback.answer()
    await state.set_state(ProviderRegistration.waiting_for_start_time)


@router.message(ProviderRegistration.waiting_for_start_time)
async def process_start_time(message: Message, state: FSMContext):
    """Process start time input"""
    if not is_valid_time_format(message.text):
        await message.answer("❌ Please enter time in HH:MM format (e.g., 09:00)")
        return
    
    start_time = parse_time(message.text)
    await state.update_data(start_time=start_time)
    
    await message.answer(
        "⏰ Enter your working hours end time (HH:MM format):\n\n"
        "Example: 18:00"
    )
    await state.set_state(ProviderRegistration.waiting_for_end_time)


@router.message(ProviderRegistration.waiting_for_end_time)
async def process_end_time(message: Message, state: FSMContext):
    """Process end time input"""
    if not is_valid_time_format(message.text):
        await message.answer("❌ Please enter time in HH:MM format (e.g., 18:00)")
        return
    
    end_time = parse_time(message.text)
    data = await state.get_data()
    start_time = data.get("start_time")
    
    if end_time <= start_time:
        await message.answer("❌ End time must be after start time.")
        return
    
    await state.update_data(end_time=end_time)
    
    await message.answer(
        "⏱️ Enter slot duration in minutes (default is 30):\n\n"
        "Example: 30, 45, or 60"
    )
    await state.set_state(ProviderRegistration.waiting_for_slot_duration)


@router.message(ProviderRegistration.waiting_for_slot_duration)
async def process_slot_duration(message: Message, state: FSMContext):
    """Process slot duration and complete registration"""
    try:
        duration = int(message.text)
        if duration < 15 or duration > 120:
            await message.answer("❌ Duration must be between 15 and 120 minutes.")
            return
    except ValueError:
        await message.answer("❌ Please enter a valid number.")
        return
    
    data = await state.get_data()
    
    # Create user and provider records
    async with get_db() as db:
        # Create user
        user = User(
            telegram_id=message.from_user.id,
            full_name=data["full_name"],
            role="provider",
            phone=data.get("phone")
        )
        db.add(user)
        await db.flush()  # Get user ID
        
        # Create provider
        provider = Provider(
            user_id=user.id,
            service_id=data["service_id"],
            location=data["location"],
            working_days=data["working_days"],
            working_hours_start=data["start_time"],
            working_hours_end=data["end_time"],
            slot_duration=duration
        )
        db.add(provider)
        await db.commit()
    
    await message.answer(
        f"🎉 Registration completed successfully!\n\n"
        f"Welcome, {data['full_name']}! Your provider profile has been created.\n\n"
        f"You can now manage your bookings and schedule.",
        reply_markup=get_provider_menu_keyboard()
    )
    await state.clear()


@router.message(F.text == "📋 My Bookings")
async def show_provider_bookings(message: Message):
    """Show provider's bookings"""
    async with get_db() as db:
        # Get provider
        result = await db.execute(
            select(Provider).where(Provider.user_id == 
                select(User.id).where(User.telegram_id == message.from_user.id)
            )
        )
        provider = result.scalar_one_or_none()
        
        if not provider:
            await message.answer("❌ Provider profile not found.")
            return
        
        # Get bookings
        result = await db.execute(
            select(Booking, Slot, User)
            .join(Slot, Booking.slot_id == Slot.id)
            .join(User, Booking.client_id == User.id)
            .where(Slot.provider_id == provider.id)
            .where(Booking.status == "active")
            .order_by(Slot.date, Slot.time)
        )
        bookings = result.all()
    
    if not bookings:
        await message.answer(
            "📅 You have no active bookings yet.\n\n"
            "Bookings will appear here when clients book your services."
        )
        return
    
    text = "📋 Your Active Bookings:\n\n"
    for booking, slot, client in bookings:
        status_emoji = get_emoji_for_status(booking.status)
        formatted_date = format_date(slot.date)
        
        text += f"{status_emoji} **{client.full_name}**\n"
        text += f"📅 {formatted_date} at {slot.time}\n"
        text += f"🔧 {provider.service.name}\n\n"
    
    await message.answer(text, parse_mode="Markdown")


@router.message(F.text == "📅 Manage Schedule")
async def manage_schedule(message: Message):
    """Show schedule management options"""
    async with get_db() as db:
        result = await db.execute(
            select(Provider).where(Provider.user_id == 
                select(User.id).where(User.telegram_id == message.from_user.id)
            )
        )
        provider = result.scalar_one_or_none()
    
    if not provider:
        await message.answer("❌ Provider profile not found.")
        return
    
    working_days = [get_weekday_name(d) for d in (provider.working_days or [])]
    days_text = ", ".join(working_days) if working_days else "None"
    
    text = f"""
📅 **Your Current Schedule:**

🕐 Working Hours: {format_time(provider.working_hours_start)} - {format_time(provider.working_hours_end)}
📅 Working Days: {days_text}
⏱️ Slot Duration: {provider.slot_duration} minutes
📍 Location: {provider.location or 'Not specified'}

⚙️ **Settings:**
"""
    
    keyboard = get_availability_toggle_keyboard(provider.is_accepting)
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "pause_bookings")
async def pause_bookings(callback: CallbackQuery):
    """Pause accepting new bookings"""
    async with get_db() as db:
        await db.execute(
            update(Provider)
            .where(Provider.user_id == 
                select(User.id).where(User.telegram_id == callback.from_user.id)
            )
            .values(is_accepting=False)
        )
        await db.commit()
    
    await callback.message.edit_text(
        "🛑 You have paused accepting new bookings.\n\n"
        "Clients will not be able to book new appointments until you resume.",
        reply_markup=get_availability_toggle_keyboard(False)
    )
    await callback.answer("Bookings paused!")


@router.callback_query(F.data == "resume_bookings")
async def resume_bookings(callback: CallbackQuery):
    """Resume accepting new bookings"""
    async with get_db() as db:
        await db.execute(
            update(Provider)
            .where(Provider.user_id == 
                select(User.id).where(User.telegram_id == callback.from_user.id)
            )
            .values(is_accepting=True)
        )
        await db.commit()
    
    await callback.message.edit_text(
        "✅ You are now accepting new bookings!\n\n"
        "Clients can book appointments with you again.",
        reply_markup=get_availability_toggle_keyboard(True)
    )
    await callback.answer("Bookings resumed!")


@router.message(F.text == "📊 Dashboard")
async def show_dashboard(message: Message):
    """Show provider dashboard"""
    async with get_db() as db:
        # Get provider
        result = await db.execute(
            select(Provider).where(Provider.user_id == 
                select(User.id).where(User.telegram_id == message.from_user.id)
            )
        )
        provider = result.scalar_one_or_none()
        
        if not provider:
            await message.answer("❌ Provider profile not found.")
            return
        
        # Get stats
        today = get_today_str()
        
        # Today's bookings
        today_bookings = await db.execute(
            select(Booking, Slot)
            .join(Slot, Booking.slot_id == Slot.id)
            .where(Slot.provider_id == provider.id)
            .where(Slot.date == today)
            .where(Booking.status == "active")
        )
        today_count = len(today_bookings.all())
        
        # Total active bookings
        total_bookings = await db.execute(
            select(Booking, Slot)
            .join(Slot, Booking.slot_id == Slot.id)
            .where(Slot.provider_id == provider.id)
            .where(Booking.status == "active")
        )
        total_count = len(total_bookings.all())
    
    text = f"""
📊 **Your Dashboard**

📅 Today's Appointments: {today_count}
📋 Total Active Bookings: {total_count}
🔧 Service: {provider.service.name}
📍 Location: {provider.location or 'Not specified'}
🟢 Status: {'Accepting bookings' if provider.is_accepting else 'Paused'}

Keep up the great work! 💪
"""
    
    await message.answer(text, parse_mode="Markdown")
