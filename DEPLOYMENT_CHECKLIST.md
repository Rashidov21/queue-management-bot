# 🚀 Deployment Checklist

Use this checklist to ensure a smooth deployment to PythonAnywhere.

## ✅ Pre-Deployment

- [ ] **Repository is ready**
  - [ ] All code is committed and pushed to GitHub
  - [ ] `.env` file is created from `env.example`
  - [ ] Environment variables are configured
  - [ ] No sensitive data in the repository

- [ ] **PythonAnywhere account**
  - [ ] Account is created and verified
  - [ ] Web app is created
  - [ ] Domain is configured (if using custom domain)

- [ ] **Telegram Bot**
  - [ ] Bot is created with @BotFather
  - [ ] Bot token is obtained
  - [ ] Bot is configured with commands (optional)

## ✅ Initial Setup

- [ ] **Clone repository**
  ```bash
  git clone https://github.com/yourusername/queue-management-bot.git
  cd queue-management-bot
  ```

- [ ] **Install dependencies**
  ```bash
  pip3.10 install --user -r requirements.txt
  ```

- [ ] **Configure environment**
  ```bash
  cp env.example .env
  nano .env  # Update with your values
  ```

- [ ] **Run setup script**
  ```bash
  python3.10 manage_pythonanywhere.py setup
  ```

- [ ] **Update WSGI file**
  ```bash
  sed -i 's/yourusername/your-actual-username/g' wsgi.py
  ```

## ✅ Web App Configuration

- [ ] **Source code path**: `/home/yourusername/queue-management-bot`
- [ ] **Working directory**: `/home/yourusername/queue-management-bot`
- [ ] **WSGI file**: `/home/yourusername/queue-management-bot/wsgi.py`

- [ ] **Static files mapping**
  - URL: `/static/`
  - Directory: `/home/yourusername/queue-management-bot/staticfiles`

- [ ] **Media files mapping** (if needed)
  - URL: `/media/`
  - Directory: `/home/yourusername/queue-management-bot/media`

## ✅ Database Setup

- [ ] **SQLite (Default)**
  - [ ] Database file is created
  - [ ] Migrations are applied
  - [ ] Superuser is created

- [ ] **PostgreSQL (Optional)**
  - [ ] Database is created in PythonAnywhere
  - [ ] Database URL is configured in `.env`
  - [ ] Migrations are applied

## ✅ Security Configuration

- [ ] **Environment variables**
  - [ ] `DEBUG=False`
  - [ ] `SECRET_KEY` is set to a secure value
  - [ ] `ALLOWED_HOSTS` includes your domain
  - [ ] `TELEGRAM_BOT_TOKEN` is set
  - [ ] `TELEGRAM_WEBHOOK_URL` is set

- [ ] **HTTPS configuration**
  - [ ] SSL certificate is configured
  - [ ] All HTTP traffic redirects to HTTPS

## ✅ Telegram Bot Setup

- [ ] **Webhook configuration**
  ```bash
  python3.10 manage.py setup_webhook
  ```

- [ ] **Test webhook**
  - [ ] Send a message to your bot
  - [ ] Check if the message is received
  - [ ] Verify webhook is working

## ✅ Testing

- [ ] **Web application**
  - [ ] Home page loads correctly
  - [ ] User registration works
  - [ ] User login works
  - [ ] Dashboard loads for providers
  - [ ] Booking system works

- [ ] **API endpoints**
  - [ ] API root is accessible
  - [ ] User registration API works
  - [ ] Telegram login API works
  - [ ] All endpoints return proper responses

- [ ] **Telegram bot**
  - [ ] Bot responds to commands
  - [ ] Webhook receives updates
  - [ ] Notifications are sent correctly

## ✅ GitHub Actions Setup

- [ ] **Repository secrets**
  - [ ] `PYTHONANYWHERE_API_TOKEN` is set
  - [ ] `PYTHONANYWHERE_USERNAME` is set
  - [ ] `PYTHONANYWHERE_DOMAIN` is set

- [ ] **Workflow is working**
  - [ ] Tests pass on push
  - [ ] Deployment works on main branch
  - [ ] Linting passes

## ✅ Monitoring

- [ ] **Logs are accessible**
  - [ ] Error logs are checked
  - [ ] No critical errors found
  - [ ] Log rotation is configured

- [ ] **Performance monitoring**
  - [ ] Response times are acceptable
  - [ ] Memory usage is within limits
  - [ ] Database queries are optimized

## ✅ Backup

- [ ] **Database backup**
  - [ ] Regular backups are configured
  - [ ] Backup files are stored securely
  - [ ] Restore procedure is tested

- [ ] **Code backup**
  - [ ] Repository is backed up
  - [ ] Environment files are secured
  - [ ] Deployment scripts are versioned

## ✅ Documentation

- [ ] **Deployment documentation**
  - [ ] README is updated
  - [ ] Deployment guide is complete
  - [ ] Troubleshooting guide is available

- [ ] **User documentation**
  - [ ] User guide is available
  - [ ] API documentation is complete
  - [ ] Bot commands are documented

## ✅ Go Live

- [ ] **Final checks**
  - [ ] All tests pass
  - [ ] No errors in logs
  - [ ] All features work correctly
  - [ ] Performance is acceptable

- [ ] **Announcement**
  - [ ] Users are notified
  - [ ] Documentation is published
  - [ ] Support channels are ready

## 🚨 Emergency Procedures

- [ ] **Rollback plan**
  - [ ] Previous version is available
  - [ ] Database rollback procedure
  - [ ] Webhook rollback procedure

- [ ] **Contact information**
  - [ ] Support team contacts
  - [ ] Emergency procedures
  - [ ] Escalation process

---

**✅ Deployment Complete!**

Your Queue Management Bot is now live on PythonAnywhere! 🎉

**Next Steps:**
1. Monitor the application for any issues
2. Set up regular backups
3. Monitor performance and usage
4. Plan for scaling as needed
5. Keep the application updated

**Useful Commands:**
- `python3.10 manage_pythonanywhere.py status` - Check status
- `python3.10 manage_pythonanywhere.py update` - Update application
- `python3.10 manage.py setup_webhook` - Configure webhook
- `python3.10 manage.py shell` - Django shell access
