# 🔍 GitHub Finder Telegram Bot

A high-performance Telegram bot that searches GitHub code, filenames, and repositories directly from chat. Includes a built-in Flask health check server to keep the service active 24/7 on free cloud platforms.

---

## ✨ Features

- **Exact Content Search (`/repo <query>`)**: Uses GitHub's code search API to locate matching lines inside raw repository files.
- **Filename Search (`/filename <name>`)**: Finds files across repositories that match a target filename.
- **Repository Search (`/advrepo <name>`)**: Finds matching repository names.
- **Health Check Endpoint (`/` & `/health`)**: Responds with `200 OK` for UptimeRobot, Render, or cron pings.
- **Smart Splitting**: Automatically divides messages exceeding Telegram's 4096-character limit.

---

## 🛠️ Prerequisites

Before running, obtain the required tokens:

1. **Telegram Bot Token**: Get one from [@BotFather](https://t.me/BotFather).
2. **GitHub Personal Access Token**: Generate a token at [GitHub Developer Settings](https://github.com/settings/tokens) (a classic token with `public_repo` or `read:packages` scope).

Create a `.env` file in the project root:
```env
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
GITHUB_TOKEN=ghp_YourGitHubPersonalAccessTokenHere
PORT=8080

🚀 Deployment Options
1. Local Machine (Windows / Mac / Linux)
# Clone the repository
git clone [https://github.com/your-username/github-finder-bot.git](https://github.com/your-username/github-finder-bot.git)
cd github-finder-bot

# Set up a virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

2. Render (Free Cloud Hosting)
Render provides free hosting with automated web service detection.
 * Push your project files (main.py, requirements.txt, .gitignore) to GitHub.
 * Log into the Render Dashboard.
 * Click New + > Web Service.
 * Connect your GitHub repository.
 * Configure the settings:
   * Environment: Python 3
   * Build Command: pip install -r requirements.txt
   * Start Command: python main.py
 * Under Environment Variables, add:
   * BOT_TOKEN: Your Telegram Bot token
   * GITHUB_TOKEN: Your GitHub token
   * PORT: 10000 (or leave default, Render sets this automatically)
 * Click Create Web Service.
Keep-Alive Tip: Render's free tier spins down after 15 minutes of inactivity. Set up a free HTTP monitor at UptimeRobot pointing to your Render URL (https://your-bot-name.onrender.com/health) with a 5-minute interval.
3. Termux (Android)
Run the bot directly from your Android phone:
# Update package lists
pkg update && pkg upgrade -y

# Install git and Python
pkg install git python -y

# Clone repo and enter directory
git clone [https://github.com/your-username/github-finder-bot.git](https://github.com/your-username/github-finder-bot.git)
cd github-finder-bot

# Install requirements
pip install -r requirements.txt

# Create .env file
nano .env

# Run the bot
python main.py

To keep it running in the background:
termux-wake-lock
nohup python main.py > bot.log 2>&1 &

4. Linux VPS (Ubuntu / Debian)
Using systemd ensures the bot automatically restarts if it crashes or the server reboots.
Step 1: Set up files
# Update server packages
sudo apt update && sudo apt install -y python3-pip python3-venv git

# Clone repository
git clone [https://github.com/your-username/github-finder-bot.git](https://github.com/your-username/github-finder-bot.git) /opt/github-finder-bot
cd /opt/github-finder-bot

# Create virtual environment and install packages
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create environment configuration
nano .env

Step 2: Configure Systemd Service
Create a systemd unit file at /etc/systemd/system/github-bot.service with the following content:
[Unit]
Description=GitHub Finder Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/github-finder-bot
ExecStart=/opt/github-finder-bot/venv/bin/python /opt/github-finder-bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

Step 3: Start and Enable Service
# Reload systemd daemon
sudo systemctl daemon-reload

# Start the bot
sudo systemctl start github-bot

# Enable auto-start on boot
sudo systemctl enable github-bot

# Check bot status and logs
sudo systemctl status github-bot
journalctl -u github-bot -f

📖 Bot Commands
| Command | Usage Example | Action |
|---|---|---|
| /start | /start | Displays welcome and usage menu |
| /repo | /repo import requests | Searches for exact text inside repo code files |
| /filename | /filename config.json | Finds repositories containing specific file names |
| /advrepo | /advrepo telegram-bot | Finds repositories matching the name query |
🔒 Security Best Practices
 * Never commit your .env file to public GitHub repositories.
 * Add .env to your .gitignore:
.env
venv/
__pycache__/
*.log


