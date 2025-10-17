import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for sending Telegram messages"""
    
    def __init__(self):
        self.bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, chat_id, message, parse_mode='HTML'):
        """Send a message to a Telegram user"""
        if not self.bot_token:
            logger.error("Telegram bot token not configured")
            return False
        
        if not chat_id:
            logger.error("Chat ID not provided")
            return False
        
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                logger.info(f"Message sent successfully to {chat_id}")
                return True
            else:
                logger.error(f"Telegram API error: {result.get('description')}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {e}")
            return False
    
    def send_booking_confirmation(self, booking):
        """Send booking confirmation message"""
        message = f"""
🎉 <b>Navbat tasdiqlandi!</b>

📅 <b>Sana:</b> {booking.date}
🕐 <b>Vaqt:</b> {booking.time}
👤 <b>Xizmat ko'rsatuvchi:</b> {booking.provider.user.full_name}
📍 <b>Manzil:</b> {booking.provider.location or 'Aniqlanmagan'}
📞 <b>Telefon:</b> {booking.provider.user.phone or 'Aniqlanmagan'}

<i>Navbat vaqtida kelishingizni so'raymiz!</i>
        """.strip()
        
        return self.send_message(booking.client.telegram_username, message)
    
    def send_booking_cancellation(self, booking):
        """Send booking cancellation message"""
        message = f"""
❌ <b>Navbat bekor qilindi</b>

📅 <b>Sana:</b> {booking.date}
🕐 <b>Vaqt:</b> {booking.time}
👤 <b>Xizmat ko'rsatuvchi:</b> {booking.provider.user.full_name}

<i>Navbat bekor qilindi. Yangi navbat olish uchun qayta murojaat qiling.</i>
        """.strip()
        
        return self.send_message(booking.client.telegram_username, message)
    
    def send_booking_reminder(self, booking, hours_remaining):
        """Send booking reminder message"""
        emoji_map = {
            72: "⏰",
            36: "⏰", 
            24: "⏰",
            3: "⚠️",
            1: "🚨"
        }
        
        emoji = emoji_map.get(hours_remaining, "⏰")
        
        message = f"""
{emoji} <b>Navbat eslatmasi</b>

📅 <b>Sana:</b> {booking.date}
🕐 <b>Vaqt:</b> {booking.time}
👤 <b>Xizmat ko'rsatuvchi:</b> {booking.provider.user.full_name}
📍 <b>Manzil:</b> {booking.provider.location or 'Aniqlanmagan'}
⏳ <b>Qolgan vaqt:</b> {hours_remaining} soat

<i>Navbat vaqtida kelishingizni so'raymiz!</i>
        """.strip()
        
        return self.send_message(booking.client.telegram_username, message)
    
    def send_provider_notification(self, provider, message):
        """Send notification to provider"""
        return self.send_message(provider.user.telegram_username, message)
    
    def send_provider_next_queue(self, booking):
        """Send next queue notification to provider"""
        message = f"""
🔔 <b>Keyingi navbat eslatmasi</b>

📅 <b>Sana:</b> {booking.date}
🕐 <b>Vaqt:</b> {booking.time}
👤 <b>Mijoz:</b> {booking.client.full_name}
📞 <b>Telefon:</b> {booking.client.phone or 'Aniqlanmagan'}
📝 <b>Izoh:</b> {booking.notes or 'Izoh yo\'q'}

<i>1 soatdan keyin navbat boshlanadi!</i>
        """.strip()
        
        return self.send_message(booking.provider.user.telegram_username, message)
    
    def send_provider_today_queues(self, provider, bookings):
        """Send today's queues to provider"""
        message = f"""
📋 <b>Bugungi navbatlar</b>

👤 <b>Xizmat ko'rsatuvchi:</b> {provider.user.full_name}
📅 <b>Sana:</b> {bookings.first().date if bookings else 'N/A'}

"""
        
        for booking in bookings:
            status_emoji = {
                'pending': '⏳',
                'confirmed': '✅',
                'active': '🟢'
            }.get(booking.status, '❓')
            
            message += f"{status_emoji} <b>{booking.time}</b> - {booking.client.full_name}\n"
        
        message += "\n<i>Bugungi navbatlar ro'yxati!</i>"
        
        return self.send_message(provider.user.telegram_username, message)
