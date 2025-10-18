"""
Django management command to set up Telegram webhook
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Set up Telegram webhook for the bot'

    def add_arguments(self, parser):
        parser.add_argument(
            '--token',
            type=str,
            help='Telegram bot token (overrides settings)',
        )
        parser.add_argument(
            '--url',
            type=str,
            help='Webhook URL (overrides settings)',
        )
        parser.add_argument(
            '--remove',
            action='store_true',
            help='Remove the webhook',
        )

    def handle(self, *args, **options):
        token = options.get('token') or settings.TELEGRAM_BOT_TOKEN
        webhook_url = options.get('url') or settings.TELEGRAM_WEBHOOK_URL
        
        if not token:
            self.stdout.write(
                self.style.ERROR('Telegram bot token not found. Please set TELEGRAM_BOT_TOKEN in your environment.')
            )
            return
        
        if not webhook_url and not options.get('remove'):
            self.stdout.write(
                self.style.ERROR('Webhook URL not found. Please set TELEGRAM_WEBHOOK_URL in your environment.')
            )
            return
        
        if options.get('remove'):
            self.remove_webhook(token)
        else:
            self.setup_webhook(token, webhook_url)

    def setup_webhook(self, token, webhook_url):
        """Set up the Telegram webhook"""
        url = f"https://api.telegram.org/bot{token}/setWebhook"
        
        data = {
            'url': webhook_url,
            'allowed_updates': ['message', 'callback_query']
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('ok'):
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Webhook set up successfully: {webhook_url}')
                )
                self.stdout.write(f'Description: {result.get("description", "No description")}')
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Failed to set webhook: {result.get("description", "Unknown error")}')
                )
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Network error: {str(e)}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Unexpected error: {str(e)}')
            )

    def remove_webhook(self, token):
        """Remove the Telegram webhook"""
        url = f"https://api.telegram.org/bot{token}/deleteWebhook"
        
        try:
            response = requests.post(url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('ok'):
                self.stdout.write(
                    self.style.SUCCESS('✅ Webhook removed successfully')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Failed to remove webhook: {result.get("description", "Unknown error")}')
                )
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Network error: {str(e)}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Unexpected error: {str(e)}')
            )
