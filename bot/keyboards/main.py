from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Main menu keyboard for role selection"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="💇‍♂️ I'm a Service Provider"))
    builder.add(KeyboardButton(text="🙋‍♀️ I'm a Client"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def get_back_keyboard() -> ReplyKeyboardMarkup:
    """Simple back button keyboard"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🔙 Back"))
    return builder.as_markup(resize_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Cancel button keyboard"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="❌ Cancel"))
    return builder.as_markup(resize_keyboard=True)


def get_working_days_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting working days"""
    builder = InlineKeyboardBuilder()
    days = [
        ("Monday", "day_0"),
        ("Tuesday", "day_1"),
        ("Wednesday", "day_2"),
        ("Thursday", "day_3"),
        ("Friday", "day_4"),
        ("Saturday", "day_5"),
        ("Sunday", "day_6")
    ]
    
    for day, callback_data in days:
        builder.add(InlineKeyboardButton(text=day, callback_data=callback_data))
    
    builder.add(InlineKeyboardButton(text="✅ Done", callback_data="days_done"))
    builder.adjust(2)
    return builder.as_markup()


def get_provider_menu_keyboard() -> ReplyKeyboardMarkup:
    """Provider main menu keyboard"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📋 My Bookings"))
    builder.add(KeyboardButton(text="📅 Manage Schedule"))
    builder.add(KeyboardButton(text="⚙️ Settings"))
    builder.add(KeyboardButton(text="📊 Dashboard"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_client_menu_keyboard() -> ReplyKeyboardMarkup:
    """Client main menu keyboard"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🔍 Book Service"))
    builder.add(KeyboardButton(text="📋 My Bookings"))
    builder.add(KeyboardButton(text="ℹ️ Help"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_services_keyboard(services: list) -> InlineKeyboardMarkup:
    """Keyboard for selecting services"""
    builder = InlineKeyboardBuilder()
    
    for service in services:
        builder.add(InlineKeyboardButton(
            text=f"🔧 {service.name}",
            callback_data=f"service_{service.id}"
        ))
    
    builder.add(InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu"))
    builder.adjust(1)
    return builder.as_markup()


def get_providers_keyboard(providers: list) -> InlineKeyboardMarkup:
    """Keyboard for selecting providers"""
    builder = InlineKeyboardBuilder()
    
    for provider in providers:
        status_emoji = "🟢" if provider.is_accepting else "🔴"
        text = f"{status_emoji} {provider.user.full_name}"
        if provider.location:
            text += f" ({provider.location})"
        
        builder.add(InlineKeyboardButton(
            text=text,
            callback_data=f"provider_{provider.id}"
        ))
    
    builder.add(InlineKeyboardButton(text="🔙 Back", callback_data="back_to_services"))
    builder.adjust(1)
    return builder.as_markup()


def get_date_keyboard(dates: list) -> InlineKeyboardMarkup:
    """Keyboard for selecting dates"""
    builder = InlineKeyboardBuilder()
    
    for date in dates:
        formatted_date = format_date(date) if hasattr(format_date, '__call__') else date
        builder.add(InlineKeyboardButton(
            text=formatted_date,
            callback_data=f"date_{date}"
        ))
    
    builder.add(InlineKeyboardButton(text="🔙 Back", callback_data="back_to_providers"))
    builder.adjust(2)
    return builder.as_markup()


def get_time_slots_keyboard(slots: list, date: str) -> InlineKeyboardMarkup:
    """Keyboard for selecting time slots"""
    builder = InlineKeyboardBuilder()
    
    for slot in slots:
        status_emoji = "🟢" if slot.status == "available" else "🔴"
        text = f"{status_emoji} {slot.time}"
        
        callback_data = f"slot_{slot.id}" if slot.status == "available" else "slot_unavailable"
        builder.add(InlineKeyboardButton(
            text=text,
            callback_data=callback_data
        ))
    
    builder.add(InlineKeyboardButton(text="🔙 Back", callback_data="back_to_dates"))
    builder.adjust(3)
    return builder.as_markup()


def get_booking_confirmation_keyboard(booking_id: int) -> InlineKeyboardMarkup:
    """Keyboard for booking confirmation"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Confirm", callback_data=f"confirm_{booking_id}"))
    builder.add(InlineKeyboardButton(text="❌ Cancel", callback_data=f"cancel_{booking_id}"))
    return builder.as_markup()


def get_booking_management_keyboard(booking_id: int) -> InlineKeyboardMarkup:
    """Keyboard for managing existing bookings"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="❌ Cancel Booking", callback_data=f"cancel_booking_{booking_id}"))
    builder.add(InlineKeyboardButton(text="📞 Contact Provider", callback_data=f"contact_{booking_id}"))
    return builder.as_markup()


def get_availability_toggle_keyboard(is_accepting: bool) -> InlineKeyboardMarkup:
    """Keyboard for toggling provider availability"""
    builder = InlineKeyboardBuilder()
    
    if is_accepting:
        builder.add(InlineKeyboardButton(text="🛑 Pause Bookings", callback_data="pause_bookings"))
    else:
        builder.add(InlineKeyboardButton(text="✅ Resume Bookings", callback_data="resume_bookings"))
    
    return builder.as_markup()


def format_date(date_str: str) -> str:
    """Helper function to format date string"""
    try:
        from datetime import datetime
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%b %d")
    except ValueError:
        return date_str
