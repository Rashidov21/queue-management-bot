from datetime import datetime, timedelta, time
from typing import List, Optional
import re


def format_time(time_obj: time) -> str:
    """Format time object to HH:MM string"""
    return time_obj.strftime("%H:%M")


def parse_time(time_str: str) -> Optional[time]:
    """Parse HH:MM string to time object"""
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        return None


def format_date(date_str: str) -> str:
    """Format date string YYYY-MM-DD to readable format"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%B %d, %Y")
    except ValueError:
        return date_str


def get_today_str() -> str:
    """Get today's date as YYYY-MM-DD string"""
    return datetime.now().strftime("%Y-%m-%d")


def get_tomorrow_str() -> str:
    """Get tomorrow's date as YYYY-MM-DD string"""
    return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")


def is_valid_time_format(time_str: str) -> bool:
    """Check if time string is in HH:MM format"""
    pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
    return bool(re.match(pattern, time_str))


def get_weekday_name(day_number: int) -> str:
    """Convert day number (0=Monday) to weekday name"""
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return weekdays[day_number] if 0 <= day_number <= 6 else "Unknown"


def generate_time_slots(start_time: time, end_time: time, duration_minutes: int = 30) -> List[str]:
    """Generate list of time slots between start and end time"""
    slots = []
    current = datetime.combine(datetime.today(), start_time)
    end = datetime.combine(datetime.today(), end_time)
    
    while current < end:
        slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=duration_minutes)
    
    return slots


def is_future_datetime(date_str: str, time_str: str) -> bool:
    """Check if given date and time is in the future"""
    try:
        datetime_str = f"{date_str} {time_str}"
        target = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        return target > datetime.now()
    except ValueError:
        return False


def get_emoji_for_status(status: str) -> str:
    """Get emoji for booking/slot status"""
    status_emojis = {
        "active": "✅",
        "available": "🟢",
        "booked": "🔴",
        "cancelled": "❌",
        "completed": "✅",
        "unavailable": "⚫"
    }
    return status_emojis.get(status, "❓")


def format_booking_message(client_name: str, provider_name: str, service_name: str, date: str, time: str) -> str:
    """Format booking confirmation message"""
    formatted_date = format_date(date)
    return f"""
🎉 Booking Confirmed!

👤 Client: {client_name}
💼 Provider: {provider_name}
🔧 Service: {service_name}
📅 Date: {formatted_date}
⏰ Time: {time}

See you soon! 😊
"""


def format_reminder_message(client_name: str, provider_name: str, service_name: str, time: str) -> str:
    """Format reminder message"""
    return f"""
⏰ Reminder!

You have an appointment with {provider_name} at {time}
Service: {service_name}

See you soon! 😊
"""
