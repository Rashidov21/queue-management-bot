"""
Telegram bot handlers for the queue management system
"""

import logging
import json
from telegram import Update
from telegram.ext import ContextTypes
from django.conf import settings

logger = logging.getLogger(__name__)

def process_telegram_update(data):
    """Process incoming Telegram update"""
    try:
        # Extract message information
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            user = message.get('from', {})
            
            # Log the message
            logger.info(f"Received message from {user.get('first_name', 'Unknown')}: {text}")
            
            # Process commands
            if text.startswith('/'):
                return process_command(text, chat_id, user)
            else:
                return process_message(text, chat_id, user)
        
        return {'status': 'processed'}
        
    except Exception as e:
        logger.error(f"Error processing Telegram update: {e}")
        return {'status': 'error', 'message': str(e)}

def process_command(command, chat_id, user):
    """Process bot commands"""
    command = command.lower()
    
    if command == '/start':
        return {
            'status': 'success',
            'message': f"""
🤖 Salom {user.get('first_name', 'Foydalanuvchi')}!

Queue Management Bot ga xush kelibsiz!

📋 Mavjud buyruqlar:
/start - Botni boshlash
/help - Yordam
/register - Ro'yxatdan o'tish
/login - Kirish
/bookings - Mening buyurtmalarim
/services - Xizmatlar ro'yxati

💡 Bot orqali xizmat buyurtma qilishingiz va buyurtmalaringizni boshqarishingiz mumkin.
            """
        }
    elif command == '/help':
        return {
            'status': 'success',
            'message': """
📖 Yordam:

🔹 /start - Botni boshlash
🔹 /help - Bu yordam xabari
🔹 /register - Yangi foydalanuvchi sifatida ro'yxatdan o'tish
🔹 /login - Tizimga kirish
🔹 /bookings - Mening buyurtmalarim
🔹 /services - Mavjud xizmatlar ro'yxati
🔹 /profile - Mening profilim
🔹 /settings - Sozlamalar

❓ Savollar uchun: @your_support_username
            """
        }
    elif command == '/register':
        return {
            'status': 'success',
            'message': """
📝 Ro'yxatdan o'tish:

Web sahifamiz orqali ro'yxatdan o'ting:
🌐 https://geekscomputer232323.pythonanywhere.com/register/

Yoki telefon raqamingizni yuboring:
📱 +998XXXXXXXXX
            """
        }
    elif command == '/login':
        return {
            'status': 'success',
            'message': """
🔐 Tizimga kirish:

Web sahifamiz orqali kiring:
🌐 https://geekscomputer232323.pythonanywhere.com/login/

Yoki telefon raqamingizni yuboring:
📱 +998XXXXXXXXX
            """
        }
    elif command == '/bookings':
        return {
            'status': 'success',
            'message': """
📋 Mening buyurtmalarim:

Web sahifamiz orqali buyurtmalaringizni ko'ring:
🌐 https://geekscomputer232323.pythonanywhere.com/bookings/

Yoki telefon raqamingizni yuboring:
📱 +998XXXXXXXXX
            """
        }
    elif command == '/services':
        return {
            'status': 'success',
            'message': """
🛠️ Mavjud xizmatlar:

Web sahifamiz orqali xizmatlarni ko'ring:
🌐 https://geekscomputer232323.pythonanywhere.com/services/

📞 Yoki telefon orqali:
+998XXXXXXXXX
            """
        }
    else:
        return {
            'status': 'success',
            'message': """
❓ Noma'lum buyruq. Yordam uchun /help buyrug'ini yuboring.
            """
        }

def process_message(text, chat_id, user):
    """Process regular messages"""
    if text.startswith('+998'):
        return {
            'status': 'success',
            'message': f"""
📱 Telefon raqam: {text}

Web sahifamiz orqali davom eting:
🌐 https://geekscomputer232323.pythonanywhere.com/
            """
        }
    else:
        return {
            'status': 'success',
            'message': """
❓ Tushunmadim. Yordam uchun /help buyrug'ini yuboring.
            """
        }

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    welcome_message = f"""
🤖 Salom {user.first_name}!

Queue Management Bot ga xush kelibsiz!

📋 Mavjud buyruqlar:
/start - Botni boshlash
/help - Yordam
/register - Ro'yxatdan o'tish
/login - Kirish
/bookings - Mening buyurtmalarim
/services - Xizmatlar ro'yxati

💡 Bot orqali xizmat buyurtma qilishingiz va buyurtmalaringizni boshqarishingiz mumkin.
    """
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_message = """
📖 Yordam:

🔹 /start - Botni boshlash
🔹 /help - Bu yordam xabari
🔹 /register - Yangi foydalanuvchi sifatida ro'yxatdan o'tish
🔹 /login - Tizimga kirish
🔹 /bookings - Mening buyurtmalarim
🔹 /services - Mavjud xizmatlar ro'yxati
🔹 /profile - Mening profilim
🔹 /settings - Sozlamalar

❓ Savollar uchun: @your_support_username
    """
    
    await update.message.reply_text(help_message)

async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /register command"""
    register_message = """
📝 Ro'yxatdan o'tish:

Web sahifamiz orqali ro'yxatdan o'ting:
🌐 https://geekscomputer232323.pythonanywhere.com/register/

Yoki telefon raqamingizni yuboring:
📱 +998XXXXXXXXX
    """
    
    await update.message.reply_text(register_message)

async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /login command"""
    login_message = """
🔐 Tizimga kirish:

Web sahifamiz orqali kiring:
🌐 https://geekscomputer232323.pythonanywhere.com/login/

Yoki telefon raqamingizni yuboring:
📱 +998XXXXXXXXX
    """
    
    await update.message.reply_text(login_message)

async def bookings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /bookings command"""
    bookings_message = """
📋 Mening buyurtmalarim:

Web sahifamiz orqali buyurtmalaringizni ko'ring:
🌐 https://geekscomputer232323.pythonanywhere.com/bookings/

Yoki telefon raqamingizni yuboring:
📱 +998XXXXXXXXX
    """
    
    await update.message.reply_text(bookings_message)

async def services_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /services command"""
    services_message = """
🛠️ Mavjud xizmatlar:

Web sahifamiz orqali xizmatlarni ko'ring:
🌐 https://geekscomputer232323.pythonanywhere.com/services/

📞 Yoki telefon orqali:
+998XXXXXXXXX
    """
    
    await update.message.reply_text(services_message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages"""
    message = update.message.text
    
    if message.startswith('+998'):
        # Handle phone number
        phone_message = f"""
📱 Telefon raqam: {message}

Web sahifamiz orqali davom eting:
🌐 https://geekscomputer232323.pythonanywhere.com/
        """
        await update.message.reply_text(phone_message)
    else:
        # Handle other messages
        await update.message.reply_text("""
❓ Tushunmadim. Yordam uchun /help buyrug'ini yuboring.
        """)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
        )
