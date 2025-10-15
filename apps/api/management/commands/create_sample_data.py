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
                'name': 'Haircut',
                'description': 'Professional haircut service',
                'duration_minutes': 30
            },
            {
                'name': 'Hair Coloring',
                'description': 'Hair coloring and styling',
                'duration_minutes': 60
            },
            {
                'name': 'Manicure',
                'description': 'Nail care and manicure service',
                'duration_minutes': 45
            },
            {
                'name': 'Massage',
                'description': 'Relaxing massage therapy',
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
                'username': 'john_barber',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'role': 'provider',
                'phone': '+1234567890',
                'service': services[0],  # Haircut
                'working_days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
                'start_time': time(9, 0),
                'end_time': time(17, 0),
                'location': 'Downtown Salon',
                'description': 'Professional barber with 10 years experience'
            },
            {
                'username': 'sarah_stylist',
                'email': 'sarah@example.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'role': 'provider',
                'phone': '+1234567891',
                'service': services[1],  # Hair Coloring
                'working_days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'],
                'start_time': time(10, 0),
                'end_time': time(18, 0),
                'location': 'Beauty Studio',
                'description': 'Expert hair colorist and stylist'
            },
            {
                'username': 'mike_nailtech',
                'email': 'mike@example.com',
                'first_name': 'Mike',
                'last_name': 'Davis',
                'role': 'provider',
                'phone': '+1234567892',
                'service': services[2],  # Manicure
                'working_days': ['tuesday', 'wednesday', 'thursday', 'friday', 'saturday'],
                'start_time': time(9, 30),
                'end_time': time(17, 30),
                'location': 'Nail Studio',
                'description': 'Professional nail technician'
            },
            {
                'username': 'lisa_therapist',
                'email': 'lisa@example.com',
                'first_name': 'Lisa',
                'last_name': 'Wilson',
                'role': 'provider',
                'phone': '+1234567893',
                'service': services[3],  # Massage
                'working_days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
                'start_time': time(8, 0),
                'end_time': time(16, 0),
                'location': 'Wellness Center',
                'description': 'Licensed massage therapist'
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
                'username': 'client1',
                'email': 'client1@example.com',
                'first_name': 'Alice',
                'last_name': 'Brown',
                'role': 'client',
                'phone': '+1234567894'
            },
            {
                'username': 'client2',
                'email': 'client2@example.com',
                'first_name': 'Bob',
                'last_name': 'Green',
                'role': 'client',
                'phone': '+1234567895'
            },
            {
                'username': 'client3',
                'email': 'client3@example.com',
                'first_name': 'Carol',
                'last_name': 'White',
                'role': 'client',
                'phone': '+1234567896'
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
                'notes': 'Regular haircut'
            },
            {
                'client': clients[1],
                'provider': providers[1],
                'date': today + timedelta(days=2),
                'time': time(14, 0),
                'status': 'pending',
                'notes': 'Hair coloring - blonde highlights'
            },
            {
                'client': clients[2],
                'provider': providers[2],
                'date': today + timedelta(days=3),
                'time': time(11, 0),
                'status': 'confirmed',
                'notes': 'French manicure'
            },
            {
                'client': clients[0],
                'provider': providers[3],
                'date': today + timedelta(days=4),
                'time': time(9, 0),
                'status': 'pending',
                'notes': 'Deep tissue massage'
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
            self.style.SUCCESS('Successfully created sample data!')
        )
        self.stdout.write('\nSample accounts created:')
        self.stdout.write('Providers (username / password):')
        for provider in providers:
            self.stdout.write(f'  {provider.user.username} / password123')
        self.stdout.write('\nClients (username / password):')
        for client in clients:
            self.stdout.write(f'  {client.username} / password123')
        self.stdout.write('\nAdmin access: /admin/')
        self.stdout.write('API access: /api/')
