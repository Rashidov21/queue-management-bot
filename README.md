# 🤖 Queue Management Bot

A modern, lightweight Telegram-based queue management system with a web admin dashboard. Built with Python, aiogram 3.x, FastAPI, SQLAlchemy, and APScheduler.

## ✨ Features

### 🧑‍💼 For Service Providers
- **Easy Registration**: Quick setup with service type, location, and schedule
- **Schedule Management**: Set working days, hours, and slot duration
- **Booking Control**: Pause/resume accepting new bookings
- **Real-time Notifications**: Get notified of new bookings and cancellations
- **Booking Management**: View and manage all active bookings

### 👤 For Clients
- **Service Discovery**: Browse available services and providers
- **Smart Booking**: View only available time slots
- **Instant Confirmation**: Get immediate booking confirmation
- **Booking Management**: View and cancel your bookings
- **Reminders**: Receive friendly appointment reminders

### 🌐 For Admins
- **Web Dashboard**: Clean, modern admin interface
- **User Management**: View all users, providers, and clients
- **Service Management**: Add and manage services
- **Booking Overview**: Monitor all bookings and statistics
- **Real-time Metrics**: Dashboard with key performance indicators

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd queue-management-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your bot token and settings
   ```

4. **Set up your bot token**
   ```bash
   # In your .env file:
   BOT_TOKEN=your_telegram_bot_token_here
   ```

5. **Initialize the database and seed data**
   ```bash
   python -m database.seed
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

The bot will start in polling mode and the web admin dashboard will be available at `http://localhost:8000`.

## 📱 Usage

### For Service Providers

1. **Start the bot**: Send `/start` to your bot
2. **Register**: Choose "I'm a Service Provider"
3. **Complete profile**: Enter name, select service, add location
4. **Set schedule**: Choose working days and hours
5. **Start accepting bookings**: Your profile is now live!

### For Clients

1. **Start the bot**: Send `/start` to your bot
2. **Browse services**: Choose "I'm a Client"
3. **Select service**: Pick from available services
4. **Choose provider**: View available providers and locations
5. **Book appointment**: Select date and time slot
6. **Confirm booking**: Get instant confirmation!

### For Admins

1. **Access dashboard**: Go to `http://localhost:8000`
2. **Login**: Use admin credentials (default: admin/admin123)
3. **Manage system**: View users, services, and bookings
4. **Monitor activity**: Check dashboard for real-time metrics

## 🛠️ Configuration

### Environment Variables

```bash
# Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here
WEBHOOK_URL=https://your-domain.com  # Optional for webhook mode

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./queue_bot.db  # SQLite for development
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db  # PostgreSQL for production

# Web Configuration
WEB_HOST=0.0.0.0
WEB_PORT=8000
SECRET_KEY=your-secret-key-change-in-production

# Admin Configuration
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Notification Configuration
REMINDER_HOURS_BEFORE=1
```

### Running Modes

```bash
# Run both bot and web dashboard
python run.py

# Run only the Telegram bot
python run.py bot

# Run only the web dashboard
python run.py web

# Show help
python run.py help
```

## 🏗️ Project Structure

```
queue-management-bot/
├── bot/                    # Telegram bot code
│   ├── handlers/          # Bot message handlers
│   ├── keyboards/         # Inline keyboards
│   ├── states/           # FSM states
│   ├── utils/            # Helper functions
│   └── main.py           # Bot main file
├── web/                   # Web admin dashboard
│   ├── routes/           # FastAPI routes
│   └── main.py           # Web app main file
├── database/              # Database code
│   ├── models.py         # SQLAlchemy models
│   ├── db.py             # Database connection
│   └── seed.py           # Initial data seeding
├── config.py             # Configuration settings
├── scheduler.py          # Notification scheduler
├── run.py                # Main application runner
└── requirements.txt      # Python dependencies
```

## 🔧 Technical Details

### Database Models
- **User**: Basic user information (telegram_id, name, role)
- **Service**: Available services (haircut, massage, etc.)
- **Provider**: Service provider profiles and settings
- **Slot**: Time slots for appointments
- **Booking**: Client bookings and status

### Key Features
- **Async/Await**: Full async support for better performance
- **State Management**: FSM for handling user flows
- **Scheduled Tasks**: APScheduler for reminders and cleanup
- **Responsive UI**: Clean, emoji-enhanced interface
- **Error Handling**: Graceful error handling throughout

### Notifications
- **Booking Confirmations**: Instant notifications to both parties
- **Appointment Reminders**: 1-hour advance reminders
- **Status Updates**: Real-time booking status changes
- **Admin Alerts**: System notifications for admins

## 🚀 Deployment

### Local Development
```bash
python run.py
```

### Production Deployment

1. **Use PostgreSQL**:
   ```bash
   DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
   ```

2. **Set up webhook** (optional):
   ```bash
   WEBHOOK_URL=https://your-domain.com
   ```

3. **Use a process manager** like PM2 or systemd
4. **Set up reverse proxy** with Nginx
5. **Configure SSL** for HTTPS

### Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "run.py"]
```

## 🔐 Security Notes

- Change default admin credentials in production
- Use strong SECRET_KEY for sessions
- Enable HTTPS for web dashboard
- Regularly update dependencies
- Monitor bot usage and logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs via GitHub issues
- **Documentation**: Check this README and code comments
- **Community**: Join our discussion forums

## 🎯 Roadmap

- [ ] Multi-language support
- [ ] Advanced scheduling features
- [ ] Payment integration
- [ ] Mobile app companion
- [ ] Analytics dashboard
- [ ] API for third-party integrations

---

**Built with ❤️ using Python, aiogram, FastAPI, and modern web technologies.**
