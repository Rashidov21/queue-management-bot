# 🚀 Deployment Guide

This guide covers different deployment options for the Queue Management Bot.

## 🏠 Local Development

### Quick Start
```bash
# 1. Clone and setup
git clone <repository-url>
cd queue-management-bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run setup
python setup.py

# 4. Edit .env with your bot token
# BOT_TOKEN=your_telegram_bot_token_here

# 5. Run the application
python run.py
```

### Access Points
- **Bot**: Find your bot on Telegram and send `/start`
- **Web Admin**: http://localhost:8000 (admin/admin123)

## ☁️ Cloud Deployment

### Railway.app (Recommended)

1. **Create Railway account** and connect GitHub
2. **Create new project** from your repository
3. **Add environment variables**:
   ```
   BOT_TOKEN=your_telegram_bot_token
   DATABASE_URL=postgresql://... (auto-provided)
   SECRET_KEY=your-secret-key
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your-secure-password
   ```
4. **Deploy**: Railway will automatically deploy your app

### Render.com

1. **Create Render account** and connect GitHub
2. **Create new Web Service** from your repository
3. **Configure**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python run.py`
4. **Add environment variables** (same as Railway)
5. **Deploy**

### Heroku

1. **Create Heroku app**
2. **Add PostgreSQL addon**
3. **Set environment variables**:
   ```bash
   heroku config:set BOT_TOKEN=your_token
   heroku config:set SECRET_KEY=your_secret
   heroku config:set ADMIN_USERNAME=admin
   heroku config:set ADMIN_PASSWORD=your_password
   ```
4. **Deploy**:
   ```bash
   git push heroku main
   ```

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "run.py"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  queue-bot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - DATABASE_URL=postgresql://postgres:password@db:5432/queue_bot
      - SECRET_KEY=${SECRET_KEY}
      - ADMIN_USERNAME=${ADMIN_USERNAME}
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=queue_bot
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### Run with Docker
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 🔧 Production Configuration

### Environment Variables
```bash
# Required
BOT_TOKEN=your_telegram_bot_token_here

# Database (use PostgreSQL for production)
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# Security
SECRET_KEY=your-very-secure-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=very-secure-password

# Optional
WEBHOOK_URL=https://your-domain.com
REMINDER_HOURS_BEFORE=1
```

### Database Setup (PostgreSQL)
```sql
-- Create database
CREATE DATABASE queue_bot;

-- Create user
CREATE USER queue_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE queue_bot TO queue_user;
```

### Webhook Setup (Optional)

For production, you might want to use webhooks instead of polling:

1. **Set webhook URL**:
   ```bash
   WEBHOOK_URL=https://your-domain.com
   ```

2. **Configure reverse proxy** (Nginx example):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /webhook {
           proxy_pass http://localhost:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **SSL Certificate** (Let's Encrypt):
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

## 🔍 Monitoring & Logging

### Health Checks
- **Web**: `GET /health`
- **Bot**: Check if bot responds to `/start`

### Logging
The application logs important events:
- Bot startup/shutdown
- Database operations
- Notification sending
- Error conditions

### Monitoring Commands
```bash
# Check if bot is running
curl http://localhost:8000/health

# View logs (if using systemd)
journalctl -u queue-bot -f

# View logs (if using Docker)
docker-compose logs -f queue-bot
```

## 🔒 Security Best Practices

### Production Security
1. **Change default credentials**:
   ```bash
   ADMIN_USERNAME=your_admin_username
   ADMIN_PASSWORD=very-secure-password-here
   ```

2. **Use strong SECRET_KEY**:
   ```bash
   SECRET_KEY=$(openssl rand -hex 32)
   ```

3. **Enable HTTPS** for web dashboard

4. **Use environment variables** for sensitive data

5. **Regular updates**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

### Bot Security
- Keep your bot token secure
- Monitor bot usage and logs
- Implement rate limiting if needed
- Regular security updates

## 🚨 Troubleshooting

### Common Issues

1. **Bot not responding**:
   - Check BOT_TOKEN is correct
   - Verify bot is running
   - Check logs for errors

2. **Database connection failed**:
   - Verify DATABASE_URL format
   - Check database is running
   - Verify credentials

3. **Web dashboard not accessible**:
   - Check port 8000 is open
   - Verify web service is running
   - Check firewall settings

4. **Notifications not working**:
   - Check scheduler is running
   - Verify bot can send messages
   - Check user permissions

### Debug Mode
```bash
# Run with debug logging
LOG_LEVEL=DEBUG python run.py

# Run only bot for testing
python run.py bot

# Run only web for testing
python run.py web
```

## 📞 Support

- **Documentation**: Check README.md
- **Issues**: GitHub Issues
- **Community**: Discussion forums

---

**Happy deploying! 🚀**
