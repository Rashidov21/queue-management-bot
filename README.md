# Queue Management Bot - Django Edition

A modern, stable Django-based queue management system with Telegram bot integration.

## 🚀 Features

- **Django 5.x** backend with REST API
- **SQLite** database (production-ready)
- **Django Admin** panel for management
- **Telegram Bot** integration
- **Modern Tailwind CSS** frontend
- **Unified startup** - bot and web server start together
- **Clean, async-ready** architecture
- **Windows-compatible** (no compilation issues)

## 📋 System Requirements

- Python 3.8+
- Django 5.x
- SQLite (included with Python)

## 🛠️ Installation

### Quick Setup (Recommended):
```bash
git clone <repository>
cd queue-management-bot
python setup.py
```

### Manual Setup:
1. **Clone and setup:**
   ```bash
   git clone <repository>
   cd queue-management-bot
   python -m venv venv
   ```

2. **Activate virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   # Copy example environment file
   cp env.example .env
   
   # Edit .env with your settings:
   BOT_TOKEN=your_telegram_bot_token_here
   SECRET_KEY=your-django-secret-key
   DEBUG=True
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create admin user:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Create sample data (optional):**
   ```bash
   python manage.py create_sample_data
   ```

## 🎯 Quick Start

### Activate Virtual Environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Start Both Bot and Web Server (Recommended):
```bash
python run_bot.py
```
This will start both the Telegram bot and Django web server simultaneously.
- Telegram Bot: Active and ready to receive messages
- Web Interface: http://localhost:8001/
- Admin Panel: http://localhost:8001/admin/
- API: http://localhost:8001/api/
- Login: admin / admin123

### Alternative: Start Services Separately:
```bash
# Start Django Server only
python run_django.py

# Start Telegram Bot only (in another terminal)
python telegram_bot.py
```

### Test Integration:
```bash
python test_integration.py
```

## 📊 API Endpoints

### Public Endpoints:
- `GET /api/services/` - List all services
- `GET /api/providers/` - List all providers
- `GET /api/providers/{id}/slots/?date=YYYY-MM-DD` - Available time slots

### Authenticated Endpoints:
- `GET /api/users/me/` - User profile
- `GET /api/bookings/` - User's bookings
- `POST /api/bookings/` - Create booking
- `GET /api/notifications/` - User notifications
- `GET /api/dashboard/stats/` - Dashboard statistics

## 🤖 Telegram Bot Commands

- `/start` - Main menu
- `📋 View Services` - Browse available services
- `📅 My Bookings` - View your bookings
- `👤 Profile` - View your profile
- `ℹ️ Help` - Show help information

## 👥 User Roles

### Clients:
- Browse services and providers
- Book appointments
- View their bookings
- Receive notifications

### Service Providers:
- Set working hours and days
- View their bookings
- Accept/reject appointments
- Manage availability

### Admins:
- Manage users, services, and providers
- View all bookings and statistics
- Configure system settings

## 🗄️ Database Models

### User (Custom)
- Extends Django's AbstractUser
- Role: client/provider
- Telegram integration

### Service
- Name, description, duration
- Active/inactive status

### Provider
- Links to User and Service
- Working days/hours
- Location and availability

### Booking
- Client, provider, date, time
- Status tracking
- Notes and history

### Notification
- User notifications
- Booking-related alerts
- Read/unread status

## 🔧 Configuration

### Environment Variables:
```env
BOT_TOKEN=your_telegram_bot_token
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

### Django Settings:
- Custom User model
- REST Framework configuration
- CORS settings for API access
- Admin panel customization

## 📱 Sample Data

The system includes sample data:
- 4 services (Haircut, Hair Coloring, Manicure, Massage)
- 4 providers with different schedules
- 3 client accounts
- Sample bookings

**Sample Accounts:**
- Providers: john_barber, sarah_stylist, mike_nailtech, lisa_therapist
- Clients: client1, client2, client3
- Password for all: `password123`

## 🚀 Production Deployment

1. **Set production settings:**
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com']
   SECRET_KEY = 'your-production-secret-key'
   ```

2. **Use PostgreSQL (recommended):**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'queue_management',
           'USER': 'your_user',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

3. **Set up webhook for bot:**
   ```python
   WEBHOOK_URL = 'https://yourdomain.com/webhook/'
   ```

## 🔍 Troubleshooting

### Common Issues:

1. **Bot not responding:**
   - Check BOT_TOKEN in .env
   - Ensure Django server is running
   - Check bot permissions

2. **Database errors:**
   - Run migrations: `python manage.py migrate`
   - Check database permissions

3. **API not working:**
   - Check Django server status
   - Verify API endpoints in browser
   - Check CORS settings

## 📈 Future Enhancements

- [ ] Real-time notifications via WebSockets
- [ ] Payment integration
- [ ] Advanced scheduling (recurring appointments)
- [ ] Multi-language support
- [ ] Mobile app integration
- [ ] Analytics dashboard
- [ ] Email notifications
- [ ] Calendar integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review Django and aiogram documentation

---

**Built with ❤️ using Django 5.x and aiogram 3.x**