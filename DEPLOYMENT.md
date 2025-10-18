# Queue Management Bot - Deployment Guide

This guide will help you deploy the Queue Management Bot to PythonAnywhere and set up CI/CD with GitHub.

## 📋 Prerequisites

- PythonAnywhere account (free or paid)
- GitHub repository
- Telegram Bot Token (from @BotFather)
- Domain name (optional, for custom domain)

## 🚀 Quick Start

### 1. Prepare Your Repository

1. **Clone your repository** to your local machine
2. **Copy the environment file**:
   ```bash
   cp env.example .env
   ```
3. **Update the .env file** with your actual values
4. **Commit and push** your changes to GitHub

### 2. PythonAnywhere Setup

#### Step 1: Create a New Web App

1. Log in to [PythonAnywhere](https://www.pythonanywhere.com)
2. Go to the **Web** tab
3. Click **Add a new web app**
4. Choose **Manual configuration**
5. Select **Python 3.10**
6. Click **Next**

#### Step 2: Configure the Web App

1. **Source code**: `/home/yourusername/queue-management-bot`
2. **Working directory**: `/home/yourusername/queue-management-bot`
3. **WSGI file**: `/home/yourusername/queue-management-bot/wsgi.py`

#### Step 3: Set Up the Project

1. **Open a Bash console** in PythonAnywhere
2. **Clone your repository**:
   ```bash
   git clone https://github.com/yourusername/queue-management-bot.git
   cd queue-management-bot
   ```

3. **Run the setup script**:
   ```bash
   python3.10 manage_pythonanywhere.py setup
   ```

4. **Update the WSGI file** with your username:
   ```bash
   sed -i 's/yourusername/your-actual-username/g' wsgi.py
   ```

#### Step 4: Configure Environment Variables

1. **Create a .env file**:
   ```bash
   cp env.example .env
   nano .env
   ```

2. **Update the .env file** with your values:
   ```env
   DEBUG=False
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=your-domain.pythonanywhere.com
   TELEGRAM_BOT_TOKEN=your-telegram-bot-token
   TELEGRAM_WEBHOOK_URL=https://your-domain.pythonanywhere.com/webhook/
   ```

#### Step 5: Configure Static Files

1. **Go to the Web tab** in PythonAnywhere
2. **Add a new static files mapping**:
   - URL: `/static/`
   - Directory: `/home/yourusername/queue-management-bot/staticfiles`

3. **Add media files mapping** (if needed):
   - URL: `/media/`
   - Directory: `/home/yourusername/queue-management-bot/media`

#### Step 6: Reload the Web App

1. **Go to the Web tab**
2. **Click the Reload button**
3. **Check the error log** if there are any issues

### 3. GitHub Actions Setup

#### Step 1: Add Secrets to GitHub

1. **Go to your GitHub repository**
2. **Click Settings → Secrets and variables → Actions**
3. **Add the following secrets**:
   - `PYTHONANYWHERE_API_TOKEN`: Your PythonAnywhere API token
   - `PYTHONANYWHERE_USERNAME`: Your PythonAnywhere username
   - `PYTHONANYWHERE_DOMAIN`: Your PythonAnywhere domain

#### Step 2: Configure the Workflow

The GitHub Actions workflow is already configured in `.github/workflows/deploy.yml`. It will:

- Run tests on every push
- Deploy to PythonAnywhere on main branch pushes
- Run linting checks

### 4. Telegram Bot Setup

#### Step 1: Create a Bot

1. **Message @BotFather** on Telegram
2. **Create a new bot**: `/newbot`
3. **Get your bot token**
4. **Add the token** to your `.env` file

#### Step 2: Set Up Webhook

1. **Update your .env file** with the webhook URL:
   ```env
   TELEGRAM_WEBHOOK_URL=https://your-domain.pythonanywhere.com/webhook/
   ```

2. **Run the webhook setup**:
   ```bash
   python3.10 manage.py setup_webhook
   ```

### 5. Database Setup

#### For SQLite (Default)
No additional setup required. The database will be created automatically.

#### For PostgreSQL (Recommended for Production)

1. **Create a PostgreSQL database** in PythonAnywhere
2. **Update your .env file**:
   ```env
   DATABASE_URL=postgresql://username:password@hostname:port/database_name
   ```

3. **Run migrations**:
   ```bash
   python3.10 manage.py migrate
   ```

## 🔧 Management Commands

### Update Your Application

```bash
python3.10 manage_pythonanywhere.py update
```

### Check Application Status

```bash
python3.10 manage_pythonanywhere.py status
```

### Restart Web App

```bash
python3.10 manage_pythonanywhere.py restart
```

### Set Up Telegram Webhook

```bash
python3.10 manage_pythonanywhere.py webhook
```

## 📊 Monitoring and Logs

### View Logs

1. **Go to the Web tab** in PythonAnywhere
2. **Click on the Error log** link
3. **Check for any errors** and fix them

### Monitor Performance

1. **Use the PythonAnywhere dashboard** to monitor resource usage
2. **Check the application logs** for performance issues
3. **Monitor the Telegram bot** for any webhook errors

## 🔒 Security Considerations

### Environment Variables

- **Never commit** your `.env` file to Git
- **Use strong passwords** for all services
- **Rotate secrets** regularly

### Django Security

- **Set DEBUG=False** in production
- **Use HTTPS** for all communications
- **Keep Django updated** to the latest version

### Telegram Bot Security

- **Keep your bot token secret**
- **Use webhook validation** to ensure requests are from Telegram
- **Monitor webhook logs** for suspicious activity

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
2. **Database Errors**: Check your database configuration
3. **Static Files**: Ensure static files are collected and mapped correctly
4. **Webhook Errors**: Verify your webhook URL and bot token

### Debug Mode

To enable debug mode temporarily:

1. **Set DEBUG=True** in your `.env` file
2. **Reload the web app**
3. **Check the error log** for detailed error messages
4. **Remember to set DEBUG=False** after debugging

### Getting Help

1. **Check the PythonAnywhere documentation**
2. **Review the Django deployment checklist**
3. **Check the Telegram Bot API documentation**
4. **Ask for help** in the PythonAnywhere community

## 📈 Scaling

### For Higher Traffic

1. **Upgrade to a paid PythonAnywhere plan**
2. **Use PostgreSQL** instead of SQLite
3. **Implement caching** with Redis
4. **Use a CDN** for static files
5. **Monitor performance** and optimize queries

### For Multiple Instances

1. **Use a load balancer**
2. **Implement session storage** in Redis
3. **Use a shared database**
4. **Configure proper logging**

## 🎯 Best Practices

1. **Use environment variables** for all configuration
2. **Keep your dependencies updated**
3. **Monitor your application logs**
4. **Backup your database regularly**
5. **Test your deployment** before going live
6. **Use HTTPS** for all communications
7. **Implement proper error handling**
8. **Use version control** for all changes

## 📞 Support

If you encounter any issues:

1. **Check the logs** first
2. **Review this documentation**
3. **Search for similar issues** online
4. **Ask for help** in the community
5. **Create an issue** in the GitHub repository

---

**Happy Deploying! 🚀**
