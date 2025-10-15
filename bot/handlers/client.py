from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta

from database.models import User, Provider, Service, Booking, Slot
from database.db import async_session_maker
from bot.states.user_states import ClientBooking
from bot.keyboards.main import (
    get_services_keyboard, get_providers_keyboard, get_date_keyboard,
    get_time_slots_keyboard, get_booking_confirmation_keyboard,
    get_booking_management_keyboard, get_client_menu_keyboard
)
from bot.utils.helpers import (
    format_date, get_today_str, get_tomorrow_str, is_future_datetime,
    get_emoji_for_status, format_booking_message
)

router = Router()


@router.callback_query(F.data.startswith("service_"))
async def process_service_selection_client(callback: CallbackQuery, state: FSMContext):
    """Process service selection for client"""
    service_id = int(callback.data.split("_")[1])
    await state.update_data(service_id=service_id)
    
    # Get service info
    async with async_session_maker() as db:
        result = await db.execute(select(Service).where(Service.id == service_id))
        service = result.scalar_one_or_none()
    
    if not service:
        await callback.message.edit_text("❌ Service not found.")
        await callback.answer()
        return
    
    # Get available providers for this service
    async with async_session_maker() as db:
        result = await db.execute(
            select(Provider)
            .where(Provider.service_id == service_id)
            .where(Provider.is_accepting == True)
        )
        providers = result.scalars().all()
    
    if not providers:
        await callback.message.edit_text(
            f"😔 No providers available for {service.name} at the moment.\n"
            "Please try again later or choose a different service."
        )
        await callback.answer()
        return
    
    keyboard = get_providers_keyboard(providers)
    await callback.message.edit_text(
        f"👨‍🔧 Available providers for **{service.name}**:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()
    await state.set_state(ClientBooking.waiting_for_provider)


@router.callback_query(F.data.startswith("provider_"))
async def process_provider_selection(callback: CallbackQuery, state: FSMContext):
    """Process provider selection"""
    provider_id = int(callback.data.split("_")[1])
    await state.update_data(provider_id=provider_id)
    
    # Get provider info
    async with async_session_maker() as db:
        result = await db.execute(
            select(Provider, User, Service)
            .join(User, Provider.user_id == User.id)
            .join(Service, Provider.service_id == Service.id)
            .where(Provider.id == provider_id)
        )
        provider_data = result.first()
    
    if not provider_data:
        await callback.message.edit_text("❌ Provider not found.")
        await callback.answer()
        return
    
    provider, user, service = provider_data
    
    # Generate available dates (next 7 days)
    dates = []
    for i in range(7):
        date = datetime.now() + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        dates.append(date_str)
    
    keyboard = get_date_keyboard(dates)
    await callback.message.edit_text(
        f"👤 **Provider:** {user.full_name}\n"
        f"🔧 **Service:** {service.name}\n"
        f"📍 **Location:** {provider.location or 'Not specified'}\n\n"
        f"📅 Select a date:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()
    await state.set_state(ClientBooking.waiting_for_date)


@router.callback_query(F.data.startswith("date_"))
async def process_date_selection(callback: CallbackQuery, state: FSMContext):
    """Process date selection"""
    date = callback.data.split("_")[1]
    await state.update_data(date=date)
    
    data = await state.get_data()
    provider_id = data["provider_id"]
    
    # Check if user exists, create if not
    async with async_session_maker() as db:
        result = await db.execute(select(User).where(User.telegram_id == callback.from_user.id))
        user = result.scalar_one_or_none()
        
        if not user:
            # Create client user
            user = User(
                telegram_id=callback.from_user.id,
                full_name=callback.from_user.full_name or "Client",
                role="client"
            )
            db.add(user)
            await db.commit()
        
        # Get available slots for the selected date
        result = await db.execute(
            select(Slot)
            .where(Slot.provider_id == provider_id)
            .where(Slot.date == date)
            .order_by(Slot.time)
        )
        slots = result.scalars().all()
    
    if not slots:
        # Generate slots for the day
        async with async_session_maker() as db:
            result = await db.execute(select(Provider).where(Provider.id == provider_id))
            provider = result.scalar_one_or_none()
            
            if provider and provider.working_days:
                # Check if selected date is a working day
                selected_date = datetime.strptime(date, "%Y-%m-%d")
                day_of_week = selected_date.weekday()
                
                if day_of_week in provider.working_days:
                    # Generate time slots
                    from bot.utils.helpers import generate_time_slots
                    time_slots = generate_time_slots(
                        provider.working_hours_start,
                        provider.working_hours_end,
                        provider.slot_duration
                    )
                    
                    # Create slot records
                    for time_slot in time_slots:
                        slot = Slot(
                            provider_id=provider_id,
                            date=date,
                            time=time_slot,
                            status="available"
                        )
                        db.add(slot)
                    await db.commit()
                    
                    # Get the newly created slots
                    result = await db.execute(
                        select(Slot)
                        .where(Slot.provider_id == provider_id)
                        .where(Slot.date == date)
                        .order_by(Slot.time)
                    )
                    slots = result.scalars().all()
    
    if not slots:
        await callback.message.edit_text(
            "😔 No available time slots for this date.\n"
            "Please select a different date."
        )
        await callback.answer()
        return
    
    keyboard = get_time_slots_keyboard(slots, date)
    formatted_date = format_date(date)
    
    await callback.message.edit_text(
        f"📅 Available time slots for **{formatted_date}**:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()
    await state.set_state(ClientBooking.waiting_for_time)


@router.callback_query(F.data.startswith("slot_"))
async def process_slot_selection(callback: CallbackQuery, state: FSMContext):
    """Process time slot selection"""
    if callback.data == "slot_unavailable":
        await callback.answer("This slot is not available.", show_alert=True)
        return
    
    slot_id = int(callback.data.split("_")[1])
    await state.update_data(slot_id=slot_id)
    
    # Get slot and provider info
    async with async_session_maker() as db:
        result = await db.execute(
            select(Slot, Provider, User, Service)
            .join(Provider, Slot.provider_id == Provider.id)
            .join(User, Provider.user_id == User.id)
            .join(Service, Provider.service_id == Service.id)
            .where(Slot.id == slot_id)
        )
        slot_data = result.first()
    
    if not slot_data:
        await callback.message.edit_text("❌ Slot not found.")
        await callback.answer()
        return
    
    slot, provider, user, service = slot_data
    
    # Check if slot is still available
    if slot.status != "available":
        await callback.message.edit_text("❌ This slot is no longer available.")
        await callback.answer()
        return
    
    # Get client info
    async with async_session_maker() as db:
        result = await db.execute(select(User).where(User.telegram_id == callback.from_user.id))
        client = result.scalar_one_or_none()
    
    if not client:
        await callback.message.edit_text("❌ Client not found.")
        await callback.answer()
        return
    
    formatted_date = format_date(slot.date)
    
    text = f"""
✅ **Confirm Your Booking**

👤 **Client:** {client.full_name}
💼 **Provider:** {user.full_name}
🔧 **Service:** {service.name}
📅 **Date:** {formatted_date}
⏰ **Time:** {slot.time}
📍 **Location:** {provider.location or 'Not specified'}

Do you want to confirm this booking?
"""
    
    keyboard = get_booking_confirmation_keyboard(slot_id)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()
    await state.set_state(ClientBooking.waiting_for_confirmation)


@router.callback_query(F.data.startswith("confirm_"))
async def confirm_booking(callback: CallbackQuery, state: FSMContext):
    """Confirm booking"""
    slot_id = int(callback.data.split("_")[1])
    
    # Get client
    async with async_session_maker() as db:
        result = await db.execute(select(User).where(User.telegram_id == callback.from_user.id))
        client = result.scalar_one_or_none()
        
        if not client:
            await callback.message.edit_text("❌ Client not found.")
            await callback.answer()
            return
        
        # Check if slot is still available
        result = await db.execute(select(Slot).where(Slot.id == slot_id))
        slot = result.scalar_one_or_none()
        
        if not slot or slot.status != "available":
            await callback.message.edit_text("❌ This slot is no longer available.")
            await callback.answer()
            return
        
        # Create booking
        booking = Booking(
            client_id=client.id,
            slot_id=slot_id,
            status="active"
        )
        db.add(booking)
        
        # Update slot status
        slot.status = "booked"
        
        await db.commit()
        
        # Get provider info for notification
        result = await db.execute(
            select(Provider, User, Service)
            .join(User, Provider.user_id == User.id)
            .join(Service, Provider.service_id == Service.id)
            .where(Provider.id == slot.provider_id)
        )
        provider_data = result.first()
    
    if provider_data:
        provider, provider_user, service = provider_data
        
        # Send confirmation to client
        confirmation_message = format_booking_message(
            client.full_name,
            provider_user.full_name,
            service.name,
            slot.date,
            slot.time
        )
        
        await callback.message.edit_text(confirmation_message)
        
        # Send notification to provider
        try:
            # Import bot instance
            from bot.main import bot
            formatted_date = format_date(slot.date)
            notification_text = f"""
📩 New booking received!

👤 Client: {client.full_name}
📅 Date: {formatted_date}
⏰ Time: {slot.time}
🔧 Service: {service.name}

Booking confirmed! ✅
"""
            await bot.send_message(provider_user.telegram_id, notification_text)
        except Exception as e:
            print(f"Failed to send notification to provider: {e}")
    
    await callback.answer("Booking confirmed! ✅")
    await state.clear()


@router.callback_query(F.data.startswith("cancel_"))
async def cancel_booking_selection(callback: CallbackQuery, state: FSMContext):
    """Cancel booking selection"""
    await callback.message.edit_text(
        "❌ Booking cancelled.\n\n"
        "You can start a new booking anytime by clicking '🔍 Book Service' in the main menu."
    )
    await callback.answer("Booking cancelled")
    await state.clear()


@router.message(F.text == "🔍 Book Service")
async def start_booking(message: Message, state: FSMContext):
    """Start booking process"""
    await show_services_menu(message)
    await state.set_state(ClientBooking.waiting_for_service)


@router.message(F.text == "📋 My Bookings")
async def show_client_bookings(message: Message):
    """Show client's bookings"""
    async with async_session_maker() as db:
        result = await db.execute(select(User).where(User.telegram_id == message.from_user.id))
        client = result.scalar_one_or_none()
        
        if not client:
            await message.answer("❌ Client not found.")
            return
        
        # Get bookings
        result = await db.execute(
            select(Booking, Slot, Provider, User, Service)
            .join(Slot, Booking.slot_id == Slot.id)
            .join(Provider, Slot.provider_id == Provider.id)
            .join(User, Provider.user_id == User.id)
            .join(Service, Provider.service_id == Service.id)
            .where(Booking.client_id == client.id)
            .order_by(Slot.date, Slot.time)
        )
        bookings = result.all()
    
    if not bookings:
        await message.answer(
            "📅 You have no bookings yet.\n\n"
            "Start by clicking '🔍 Book Service' to make your first booking!"
        )
        return
    
    text = "📋 Your Bookings:\n\n"
    for booking, slot, provider, provider_user, service in bookings:
        status_emoji = get_emoji_for_status(booking.status)
        formatted_date = format_date(slot.date)
        
        text += f"{status_emoji} **{service.name}**\n"
        text += f"💼 Provider: {provider_user.full_name}\n"
        text += f"📅 {formatted_date} at {slot.time}\n"
        text += f"📍 {provider.location or 'Location not specified'}\n\n"
    
    await message.answer(text, parse_mode="Markdown")


async def show_services_menu(message: Message):
    """Show available services menu"""
    async with async_session_maker() as db:
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


@router.callback_query(F.data == "back_to_services")
async def back_to_services(callback: CallbackQuery, state: FSMContext):
    """Go back to services selection"""
    await show_services_menu(callback.message)
    await callback.answer()
    await state.set_state(ClientBooking.waiting_for_service)


@router.callback_query(F.data == "back_to_providers")
async def back_to_providers(callback: CallbackQuery, state: FSMContext):
    """Go back to providers selection"""
    data = await state.get_data()
    service_id = data.get("service_id")
    
    if not service_id:
        await callback.message.edit_text("❌ Service not found.")
        await callback.answer()
        return
    
    # Get service and providers
    async with async_session_maker() as db:
        result = await db.execute(select(Service).where(Service.id == service_id))
        service = result.scalar_one_or_none()
        
        if not service:
            await callback.message.edit_text("❌ Service not found.")
            await callback.answer()
            return
        
        result = await db.execute(
            select(Provider)
            .where(Provider.service_id == service_id)
            .where(Provider.is_accepting == True)
        )
        providers = result.scalars().all()
    
    if not providers:
        await callback.message.edit_text(
            f"😔 No providers available for {service.name} at the moment."
        )
        await callback.answer()
        return
    
    keyboard = get_providers_keyboard(providers)
    await callback.message.edit_text(
        f"👨‍🔧 Available providers for **{service.name}**:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()
    await state.set_state(ClientBooking.waiting_for_provider)


@router.callback_query(F.data == "back_to_dates")
async def back_to_dates(callback: CallbackQuery, state: FSMContext):
    """Go back to dates selection"""
    data = await state.get_data()
    provider_id = data.get("provider_id")
    
    if not provider_id:
        await callback.message.edit_text("❌ Provider not found.")
        await callback.answer()
        return
    
    # Generate available dates (next 7 days)
    dates = []
    for i in range(7):
        date = datetime.now() + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        dates.append(date_str)
    
    keyboard = get_date_keyboard(dates)
    await callback.message.edit_text("📅 Select a date:", reply_markup=keyboard)
    await callback.answer()
    await state.set_state(ClientBooking.waiting_for_date)
