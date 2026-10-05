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
