from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.services.models import Service, Provider
from apps.bookings.models import Booking
from django.utils import timezone
from datetime import date, time, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create services
        services_data = [
            {
                'name': 'Soch olish',
                'description': 'Professional soch olish xizmati',
                'duration_minutes': 30
            },
            {
                'name': 'Soch bo\'yash',
                'description': 'Soch bo\'yash va stillash xizmati',
                'duration_minutes': 60
            },
            {
                'name': 'Manikyur',
                'description': 'Tirnoq parvarishi va manikyur xizmati',
                'duration_minutes': 45
            },
            {
                'name': 'Massaj',
                'description': 'Dam olish massaji terapiyasi',
                'duration_minutes': 60
            }
        ]
        
        services = []
        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            services.append(service)
            if created:
                self.stdout.write(f'Created service: {service.name}')
        
        # Create users and providers
        providers_data = [
            {
                'username': 'ahmad_sartarosh',
                'email': 'ahmad@example.com',
                'first_name': 'Ahmad',
                'last_name': 'Karimov',
                'role': 'provider',
                'phone': '+998901234567',
                'service': services[0],  # Soch olish
                'working_days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
                'start_time': time(9, 0),
                'end_time': time(17, 0),
                'location': 'Markaziy salon',
                'description': '10 yillik tajribaga ega professional sartarosh'
            },
            {
                'username': 'zebo_stilist',
                'email': 'zebo@example.com',
                'first_name': 'Zebo',
                'last_name': 'Toshmatova',
                'role': 'provider',
                'phone': '+998901234568',
                'service': services[1],  # Soch bo'yash
                'working_days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'],
                'start_time': time(10, 0),
                'end_time': time(18, 0),
                'location': 'Go\'zallik studiyasi',
                'description': 'Soch bo\'yash va stillash bo\'yicha ekspert'
            },
            {
                'username': 'dilnoza_manikyurchi',
                'email': 'dilnoza@example.com',
                'first_name': 'Dilnoza',
                'last_name': 'Umarova',
                'role': 'provider',
                'phone': '+998901234569',
                'service': services[2],  # Manikyur
                'working_days': ['tuesday', 'wednesday', 'thursday', 'friday', 'saturday'],
                'start_time': time(9, 30),
                'end_time': time(17, 30),
                'location': 'Tirnoq studiyasi',
                'description': 'Professional tirnoq texnigi'
            },
            {
                'username': 'mariya_massajchi',
                'email': 'mariya@example.com',
                'first_name': 'Mariya',
                'last_name': 'Petrova',
                'role': 'provider',
                'phone': '+998901234570',
                'service': services[3],  # Massaj
                'working_days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
                'start_time': time(8, 0),
                'end_time': time(16, 0),
                'location': 'Salomatlik markazi',
                'description': 'Litsenziyalangan massaj terapevti'
            }
        ]
        
        providers = []
        for provider_data in providers_data:
            user, created = User.objects.get_or_create(
                username=provider_data['username'],
                defaults={
                    'email': provider_data['email'],
                    'first_name': provider_data['first_name'],
                    'last_name': provider_data['last_name'],
                    'role': provider_data['role'],
                    'phone': provider_data['phone'],
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created provider user: {user.username}')
            
            # Create provider profile
            provider, created = Provider.objects.get_or_create(
                user=user,
                defaults={
                    'service': provider_data['service'],
                    'working_days': provider_data['working_days'],
                    'start_time': provider_data['start_time'],
                    'end_time': provider_data['end_time'],
                    'location': provider_data['location'],
                    'description': provider_data['description']
                }
            )
            
            if created:
                self.stdout.write(f'Created provider profile: {provider.user.full_name}')
            
            providers.append(provider)
        
        # Create client users
        clients_data = [
            {
                'username': 'mijoz1',
                'email': 'mijoz1@example.com',
                'first_name': 'Malika',
                'last_name': 'Karimova',
                'role': 'client',
                'phone': '+998901234571'
            },
            {
                'username': 'mijoz2',
                'email': 'mijoz2@example.com',
                'first_name': 'Bobur',
                'last_name': 'Nazarov',
                'role': 'client',
                'phone': '+998901234572'
            },
            {
                'username': 'mijoz3',
                'email': 'mijoz3@example.com',
                'first_name': 'Sevara',
                'last_name': 'Toshmatova',
                'role': 'client',
                'phone': '+998901234573'
            }
        ]
        
        clients = []
        for client_data in clients_data:
            user, created = User.objects.get_or_create(
                username=client_data['username'],
                defaults=client_data
            )
            
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created client user: {user.username}')
            
            clients.append(user)
        
        # Create sample bookings
        today = timezone.now().date()
        bookings_data = [
            {
                'client': clients[0],
                'provider': providers[0],
                'date': today + timedelta(days=1),
                'time': time(10, 0),
                'status': 'confirmed',
                'notes': 'Oddiy soch olish'
            },
            {
                'client': clients[1],
                'provider': providers[1],
                'date': today + timedelta(days=2),
                'time': time(14, 0),
                'status': 'pending',
                'notes': 'Soch bo\'yash - oltin rang'
            },
            {
                'client': clients[2],
                'provider': providers[2],
                'date': today + timedelta(days=3),
                'time': time(11, 0),
                'status': 'confirmed',
                'notes': 'Fransuz manikyuri'
            },
            {
                'client': clients[0],
                'provider': providers[3],
                'date': today + timedelta(days=4),
                'time': time(9, 0),
                'status': 'pending',
                'notes': 'Chuqur massaj'
            }
        ]
        
        for booking_data in bookings_data:
            booking, created = Booking.objects.get_or_create(
                client=booking_data['client'],
                provider=booking_data['provider'],
                date=booking_data['date'],
                time=booking_data['time'],
                defaults={
                    'status': booking_data['status'],
                    'notes': booking_data['notes']
                }
            )
            
            if created:
                self.stdout.write(f'Created booking: {booking}')
        
        self.stdout.write(
            self.style.SUCCESS('Namuna ma\'lumotlar muvaffaqiyatli yaratildi!')
        )
        self.stdout.write('\nYaratilgan hisoblar:')
        self.stdout.write('Xizmat ko\'rsatuvchilar (foydalanuvchi nomi / parol):')
        for provider in providers:
            self.stdout.write(f'  {provider.user.username} / password123')
        self.stdout.write('\nMijozlar (foydalanuvchi nomi / parol):')
        for client in clients:
            self.stdout.write(f'  {client.username} / password123')
        self.stdout.write('\nAdmin kirish: /admin/')
        self.stdout.write('API kirish: /api/')
