```markdown
# 🤖 GitHub Finder Bot

A Telegram bot that searches GitHub for **exact code content**, **similar filenames**, and **similar repository names** — all from a simple chat interface.

Built with [`python-telegram-bot`](https://github.com/python-telegram-bot/python-telegram-bot), the GitHub REST API, and a small Flask server (for cloud health checks).

---

## 📖 Table of Contents

- [What It Does](#-what-it-does)
- [Commands](#-commands)
- [Use Cases](#-use-cases)
- [How It Works (Logic)](#-how-it-works-logic)
- [Requirements](#-requirements)
- [Setup (Local / VPS / Termux)](#-setup)
- [Hosting on Termux (Android)](#-hosting-on-termux-android)
- [Hosting on a VPS (Ubuntu/Debian)](#-hosting-on-a-vps-ubuntudebian)
- [Hosting on Render (Free 24/7)](#-hosting-on-render-free-247)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)
- [Security Notes](#-security-notes)
- [License](#-license)

---

## 🎯 What It Does

GitHub Finder is a Telegram bot with three search modes:

| Command | What It Searches | Match Type |
|---------|------------------|------------|
| `/repo <text>` | Files containing an exact string | 🔒 Literal substring |
| `/filename <name>` | Files by filename | 📄 Partial / fuzzy |
| `/advrepo <name>` | Repositories by name | 📁 Partial / fuzzy |

The bot authenticates to GitHub using a Personal Access Token, so it can use the higher **authenticated rate limit** (5,000 requests/hour) instead of the tiny unauthenticated limit.

---

## 💬 Commands

### `/start`
Shows the help menu with examples.

### `/repo <text>`
Searches GitHub for files that **literally contain** the given text.

```
/repo mynk
/repo 123456789
/repo https://t.me/example
```
**How it works:** Uses GitHub's `search/code` endpoint with the query wrapped in quotes (forces literal match), then downloads each candidate file and verifies the substring exists before returning the repo.

### `/filename <filename>`
Searches for files whose **name contains** the given string.

```
/filename bomber.py
/filename config.json
/filename .env
```
**How it works:** Uses `filename:<name>` search qualifier, then filters results client-side for partial matches.

### `/advrepo <reponame>`
Searches for repositories whose **name contains** the given string.

```
/advrepo mynk-api
/advrepo telegram-bot
/advrepo osint
```
**How it works:** Uses `search/repositories` with the `<name> in:name` qualifier, then filters for partial matches.

---

## 🎯 Use Cases

- **🔍 OSINT / Recon:** Find leaked API keys, tokens, URLs, or config files accidentally committed to public repos.
- **📚 Code Discovery:** Find real-world examples of a specific function, library usage, or pattern.
- **🛡️ Brand Monitoring:** Detect repos impersonating your brand or project name (`/advrepo yourbrand`).
- **🎣 Threat Hunting:** Search for known malicious strings (e.g., Telegram bot tokens, webhook URLs).
- **📄 Boilerplate Hunting:** Find starter templates by filename (`/filename Dockerfile`).
- **🧪 Learning:** See how others implemented a specific feature.

---

## 🧠 How It Works (Logic)

1. **Secrets loading:** `.env` is loaded via `python-dotenv`. `BOT_TOKEN` and `GITHUB_TOKEN` are read through `os.getenv()`.
2. **GitHub API wrapper:** `github_get()` wraps `requests.get` with proper headers (`Authorization: Bearer ...`, JSON accept, API version) and raises a clean exception on non-200 responses.
3. **Search functions:**
   - `search_exact_content()` — 2-stage: search candidates → fetch each file → verify literal substring.
   - `search_filename()` — 1-stage: search → filter partial filename match.
   - `search_advrepo()` — 1-stage: search → filter partial repo name match.
4. **Async handling:** Commands use `asyncio.to_thread()` to run blocking `requests` calls without freezing the event loop.
5. **Message chunking:** Results are split into ≤3800-character messages (Telegram limit is 4096).
6. **Health server:** A Flask app listens on `$PORT` and exposes `/` and `/health` — required for cloud platforms like Render.

---

## 📋 Requirements

- **Python 3.10+** (uses `asyncio.to_thread`)
- **pip packages:**
  ```
  python-telegram-bot
  python-dotenv
  requests
  flask
  ```
- **Telegram Bot Token** — get from [@BotFather](https://t.me/BotFather)
- **GitHub Personal Access Token (classic)** — create at https://github.com/settings/tokens
  - Recommended scopes: `public_repo` (+ `repo` if you need private search)
  - ⚠️ Code search API **requires authentication** — anonymous access isn't allowed.

---

## 🛠️ Setup

### 1. Clone / Create the Project

```bash
git clone https://github.com/yourname/github-finder-bot.git
cd github-finder-bot
```

Or create it manually:

```bash
mkdir github-finder-bot && cd github-finder-bot
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate         # Linux / macOS
# venv\Scripts\activate          # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

```bash
cp .env.example .env
nano .env
```

Fill it in:

```env
BOT_TOKEN=123456:ABC-your-telegram-bot-token
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

### 5. Run

```bash
python app.py
```

You should see:
```
🤖 GitHub Finder started...
 * Running on http://0.0.0.0:8080
```

Open Telegram → find your bot → send `/start`.

---

## 📱 Hosting on Termux (Android)

### 1. Install Termux
Get it from **F-Droid** (Play Store version is outdated).

### 2. Update & Install Python

```bash
pkg update && pkg upgrade -y
pkg install python git tmux -y
```

### 3. Setup Project

```bash
mkdir -p ~/github-finder-bot
cd ~/github-finder-bot
nano app.py           # paste the code, save with CTRL+X → Y → Enter
nano requirements.txt # paste the requirements list
nano .env             # paste your tokens
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Bot

**Quick test:**
```bash
python app.py
```

**Keep it running in background (recommended):**

```bash
# Prevent Android from killing the process
termux-wake-lock

# Run detached
nohup python app.py > bot.log 2>&1 &
```

**Or use tmux (better — survives session drops):**

```bash
tmux new -s bot
python app.py
# Press Ctrl+B, then D to detach
# Reattach later with: tmux attach -t bot
```

### 6. Check Logs

```bash
tail -f bot.log
```

### 7. Stop the Bot

```bash
pkill -f app.py
# or
tmux kill-session -t bot
```

### 8. Auto-Start on Boot (Optional)

```bash
pkg install termux-boot -y
mkdir -p ~/.termux/boot
nano ~/.termux/boot/start-bot.sh
```

Contents:

```bash
#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
cd ~/github-finder-bot
python app.py
```

```bash
chmod +x ~/.termux/boot/start-bot.sh
```

Enable **Termux:Boot** app once to register.

---

## 🖥️ Hosting on a VPS (Ubuntu/Debian)

Tested on Ubuntu 22.04 / Debian 12.

### 1. SSH Into Your VPS

```bash
ssh user@your-server-ip
```

### 2. Install Dependencies

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git -y
```

### 3. Clone the Repo

```bash
cd /opt
sudo git clone https://github.com/yourname/github-finder-bot.git
sudo chown -R $USER:$USER github-finder-bot
cd github-finder-bot
```

### 4. Setup Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Configure `.env`

```bash
nano .env
```

Paste your tokens. Save & exit.

### 6. Create a systemd Service (Recommended)

```bash
sudo nano /etc/systemd/system/githubbot.service
```

Paste:

```ini
[Unit]
Description=GitHub Finder Telegram Bot
After=network.target

[Service]
Type=simple
User=YOUR_LINUX_USER
WorkingDirectory=/opt/github-finder-bot
EnvironmentFile=/opt/github-finder-bot/.env
ExecStart=/opt/github-finder-bot/venv/bin/python app.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/githubbot.log
StandardError=append:/var/log/githubbot.log

[Install]
WantedBy=multi-user.target
```

Replace `YOUR_LINUX_USER` with your actual user (run `whoami` to check).

### 7. Enable & Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable githubbot
sudo systemctl start githubbot
sudo systemctl status githubbot
```

### 8. View Logs

```bash
sudo tail -f /var/log/githubbot.log
# or
sudo journalctl -u githubbot -f
```

### 9. Restart / Stop

```bash
sudo systemctl restart githubbot
sudo systemctl stop githubbot
```

### 🔒 Firewall (Optional)

If you don't want the Flask health port exposed publicly:

```bash
sudo ufw allow ssh
sudo ufw allow 8080/tcp   # only if you need external health checks
sudo ufw enable
```

---

## ☁️ Hosting on Render (Free 24/7)

Render's free tier requires a web service listening on a port, so this repo includes a Flask health-check server.

### 1. Push to GitHub

Create a repo and upload `app.py`, `requirements.txt`, `README.md`, `.env.example`.
**Never commit `.env`.**

### 2. Create Render Web Service

1. Go to https://dashboard.render.com
2. **New +** → **Web Service**
3. Connect your GitHub repo

### 3. Configure

| Setting | Value |
|---------|-------|
| **Name** | `github-finder-bot` |
| **Region** | Closest to you |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python app.py` |
| **Instance Type** | **Free** |

### 4. Environment Variables

Under **Advanced** → **Add Environment Variable**:

```
BOT_TOKEN      = <your telegram bot token>
GITHUB_TOKEN   = <your github PAT>
```

### 5. Health Check Path

Set **Health Check Path** to:

```
/health
```

### 6. Deploy

Click **Create Web Service**. Wait for logs to show:

```
🤖 GitHub Finder started...
 * Running on http://0.0.0.0:PORT
```

### 7. Prevent Free-Tier Sleep (Critical)

Render free services sleep after ~15 min of inactivity. Add an external pinger:

1. Sign up at https://uptimerobot.com (free)
2. **Add New Monitor**:
   - **Type:** HTTP(s)
   - **URL:** `https://your-app.onrender.com/health`
   - **Interval:** 5 minutes
3. Save.

Now UptimeRobot keeps the service awake 24/7 — your bot stays online.

---

## 📁 Project Structure

```
github-finder-bot/
├── app.py              # Main bot + Flask health server
├── requirements.txt    # Python dependencies
├── .env                # Secrets (gitignored)
├── .env.example        # Template for .env
├── .gitignore
└── README.md
```

### `.env.example`

```env
BOT_TOKEN=your_telegram_bot_token_here
GITHUB_TOKEN=your_github_personal_access_token_here
```

### `.gitignore`

```gitignore
.env
venv/
__pycache__/
*.pyc
bot.log
*.log
```

---

## 🐛 Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `BOT_TOKEN missing` | `.env` not loaded | Ensure `.env` is in the same folder as `app.py` |
| `GitHub API 401` | Bad PAT | Regenerate token; check scopes |
| `GitHub API 403` | Rate limit hit | Wait, or reduce `/repo` usage |
| `GitHub API 422` | Malformed query | Escape special chars in search term |
| Bot silent on Termux | Android killed it | Run `termux-wake-lock`, use `nohup` or `tmux` |
| Render: "No open ports" | Flask not bound | Ensure `app.py` runs Flask on `$PORT` |
| Render: bot sleeps | Free tier idle | Add UptimeRobot monitor on `/health` |

---

## 🔒 Security Notes

- **Never commit `.env`.** Add it to `.gitignore` before your first commit.
- **Rotate tokens immediately** if you ever paste them publicly (chats, screenshots, commits).
- **Use the minimum scopes** needed on your GitHub PAT.
- **`chmod 600 .env`** on servers so only your user can read it.
- Consider a **dedicated GitHub account** for scraping to isolate risk.

---

## 📜 License

MIT — free to use, modify, and distribute.

---

## 🙌 Credits

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [GitHub REST API](https://docs.github.com/en/rest)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [Flask](https://flask.palletsprojects.com/)

---

**Built with ❤️ for OSINT, learning, and code discovery.**
```
