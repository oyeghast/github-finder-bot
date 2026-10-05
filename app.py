import os
import asyncio
import threading
import requests
from flask import Flask

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN missing")
if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN missing")

API = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}

# --- Flask app for Render health checks ---
web_app = Flask(__name__)

@web_app.route('/')
@web_app.route('/health')
def health():
    return "OK", 200

# --- Your existing GitHub logic (unchanged) ---
def github_get(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params, timeout=30)
    if r.status_code != 200:
        try:
            msg = r.json().get("message", r.text)
        except Exception:
            msg = r.text
        raise Exception(f"GitHub API {r.status_code}: {msg}")
    return r.json()

def search_exact_content(query):
    results = {}
    data = github_get(f"{API}/search/code", {"q": f'"{query}"', "per_page": 100})
    for item in data.get("items", []):
        repo = item.get("repository", {})
        repo_name = repo.get("full_name")
        repo_url = repo.get("html_url")
        path = item.get("path")
        if not repo_name or not repo_url or not path:
            continue
        branch = repo.get("default_branch", "main")
        try:
            file_data = github_get(f"{API}/repos/{repo_name}/contents/{path}", {"ref": branch})
            download_url = file_data.get("download_url")
            if not download_url:
                continue
            r = requests.get(download_url, timeout=20)
            if r.status_code != 200:
                continue
            if query in r.text:
                results[repo_name] = repo_url
        except Exception:
            continue
    return results

def search_filename(filename):
    results = {}
    data = github_get(f"{API}/search/code", {"q": f"filename:{filename}", "per_page": 100})
    search_term = filename.lower()
    for item in data.get("items", []):
        path = item.get("path", "")
        actual_filename = path.split("/")[-1]
        if search_term not in actual_filename.lower():
            continue
        repo = item.get("repository", {})
        repo_name = repo.get("full_name")
        repo_url = repo.get("html_url")
        if repo_name and repo_url:
            results[repo_name] = repo_url
    return results

def search_advrepo(name):
    results = {}
    data = github_get(f"{API}/search/repositories", {"q": f"{name} in:name", "per_page": 100})
    search_term = name.lower()
    for repo in data.get("items", []):
        actual_name = repo.get("name", "")
        url = repo.get("html_url")
        if search_term not in actual_name.lower():
            continue
        if actual_name and url:
            results[actual_name] = url
    return results

async def send_results(update, results):
    if not results:
        await update.message.reply_text("❌ Koi match nahi mila.")
        return
    text = ""
    for name, url in results.items():
        line = f"📁 {name}\n🔗 {url}\n\n"
        if len(text) + len(line) > 3800:
            await update.message.reply_text(text, disable_web_page_preview=True)
            text = ""
        text += line
    if text:
        await update.message.reply_text(text, disable_web_page_preview=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 GitHub Finder\n\n"
        "🔒 Exact content:\n/repo mynk\n\n"
        "📄 Similar filename:\n/filename bomber.py\n\n"
        "📁 Similar repository name:\n/advrepo mynk-api"
    )

async def repo_command(update, context):
    if not context.args:
        await update.message.reply_text("Usage:\n/repo mynk")
        return
    query = " ".join(context.args).strip()
    status = await update.message.reply_text(f"🔎 Exact content search...\n\nQuery: {query}")
    try:
        results = await asyncio.to_thread(search_exact_content, query)
    except Exception as e:
        await status.edit_text(f"❌ Error:\n{e}")
        return
    if not results:
        await status.edit_text(f"❌ Exact match nahi mila.\n\nQuery: {query}")
        return
    await status.edit_text(f"✅ Exact matches: {len(results)}\n\nQuery: {query}")
    await send_results(update, results)

async def filename_command(update, context):
    if not context.args:
        await update.message.reply_text("Usage:\n/filename bomber.py")
        return
    filename = " ".join(context.args).strip()
    status = await update.message.reply_text(f"🔎 Filename search...\n\nQuery: {filename}")
    try:
        results = await asyncio.to_thread(search_filename, filename)
    except Exception as e:
        await status.edit_text(f"❌ Error:\n{e}")
        return
    if not results:
        await status.edit_text(f"❌ Similar filename nahi mila.\n\nQuery: {filename}")
        return
    await status.edit_text(f"✅ Filename matches: {len(results)}\n\nQuery: {filename}")
    await send_results(update, results)

async def advrepo_command(update, context):
    if not context.args:
        await update.message.reply_text("Usage:\n/advrepo mynk-api")
        return
    name = " ".join(context.args).strip()
    status = await update.message.reply_text(f"🔎 Repository name search...\n\nQuery: {name}")
    try:
        results = await asyncio.to_thread(search_advrepo, name)
    except Exception as e:
        await status.edit_text(f"❌ Error:\n{e}")
        return
    if not results:
        await status.edit_text(f"❌ Similar repository nahi mila.\n\nQuery: {name}")
        return
    await status.edit_text(f"✅ Repository matches: {len(results)}\n\nQuery: {name}")
    await send_results(update, results)

def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("repo", repo_command))
    app.add_handler(CommandHandler("filename", filename_command))
    app.add_handler(CommandHandler("advrepo", advrepo_command))
    print("🤖 GitHub Finder started...")
    app.run_polling()

# --- Entry point ---
if __name__ == "__main__":
    # Start bot in a background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Start Flask on the port Render gives us
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)
