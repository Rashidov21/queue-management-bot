# Queue Management Bot

A Django-based queue management system with Telegram bot integration.

## 🚀 Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run setup script
python setup.py
```

### 2. Run the Application
```bash
# Start development server
python run.py
```

### 3. Access the Application
- **Home:** http://localhost:8000/
- **Admin:** http://localhost:8000/admin/
- **API:** http://localhost:8000/api/

## 📋 Features

- **User Management:** Registration, login, profiles
- **Service Management:** Service providers and services
- **Booking System:** Appointment booking and management
- **Telegram Bot:** Bot integration for notifications
- **REST API:** Full API for mobile/web integration

## 🔧 Development

### Available Commands
```bash
# Start development server
python run.py

# Django shell
python manage.py shell

# Create admin user
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic
```

### Project Structure
```
queue-management-bot/
├── apps/
│   ├── users/          # User management
│   ├── services/       # Service management
│   ├── bookings/       # Booking system
│   ├── api/           # REST API
│   └── bot/           # Telegram bot
├── templates/         # HTML templates
├── static/           # Static files
├── media/            # Media files
├── run.py            # Development server
├── setup.py          # Setup script
└── requirements.txt  # Dependencies
```

## 🤖 Telegram Bot

The bot supports these commands:
- `/start` - Start the bot
- `/help` - Show help
- `/register` - User registration
- `/login` - User login
- `/bookings` - View bookings
- `/services` - View services

## 📱 API Endpoints

- `GET /api/` - API information
- `POST /api/users/register/` - User registration
- `POST /api/users/login/` - User login
- `GET /api/services/` - List services
- `GET /api/providers/` - List providers
- `POST /api/bookings/` - Create booking
- `GET /api/bookings/` - List bookings

## 🔒 Security

- User authentication and authorization
- CSRF protection
- CORS configuration
- Input validation

## 📊 Database

The project uses SQLite by default for local development. The database file is `db.sqlite3`.

## 🎯 Next Steps

1. **Test the application** by visiting http://localhost:8000
2. **Create an admin user** using the setup script
3. **Explore the API** at http://localhost:8000/api/
4. **Test the Telegram bot** (if configured)

## 🆘 Troubleshooting

### Common Issues

1. **"ModuleNotFoundError"**
   ```bash
   pip install -r requirements.txt
   ```

2. **"Database table doesn't exist"**
   ```bash
   python manage.py migrate
   ```

3. **"Static files not found"**
   ```bash
   python manage.py collectstatic
   ```

### Getting Help

If you encounter any issues:
1. Check the Django error messages
2. Verify all dependencies are installed
3. Ensure the database is migrated
4. Check the static files are collected

---

**Happy Coding! 🚀**