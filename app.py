import os
import asyncio
import threading
import requests

from flask import Flask
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

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
    "User-Agent": "GitHub-Finder-Telegram-Bot",
}


web_app = Flask(__name__)


@web_app.route("/")
@web_app.route("/health")
def health():
    return "OK", 200


def github_get(url, params=None):
    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=30,
    )

    if response.status_code != 200:
        try:
            data = response.json()
            message = data.get("message", response.text)
        except Exception:
            message = response.text

        raise Exception(
            f"GitHub API {response.status_code}: {message}"
        )

    return response.json()


def search_exact_content(query):
    results = {}

    data = github_get(
        f"{API}/search/code",
        {
            "q": f'"{query}"',
            "per_page": 100,
        },
    )

    for item in data.get("items", []):
        repo = item.get("repository", {})

        repo_name = repo.get("full_name")
        repo_url = repo.get("html_url")
        path = item.get("path")

        if not repo_name or not repo_url or not path:
            continue

        branch = repo.get("default_branch", "main")

        try:
            file_data = github_get(
                f"{API}/repos/{repo_name}/contents/{path}",
                {"ref": branch},
            )

            download_url = file_data.get("download_url")

            if not download_url:
                continue

            response = requests.get(
                download_url,
                timeout=20,
            )

            if response.status_code != 200:
                continue

            if query in response.text:
                results[repo_name] = repo_url

        except Exception:
            continue

    return results


def search_filename(filename):
    results = {}

    data = github_get(
        f"{API}/search/code",
        {
            "q": f"filename:{filename}",
            "per_page": 100,
        },
    )

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

    data = github_get(
        f"{API}/search/repositories",
        {
            "q": f"{name} in:name",
            "per_page": 100,
        },
    )

    search_term = name.lower()

    for repo in data.get("items", []):
        actual_name = repo.get("name", "")
        repo_url = repo.get("html_url")

        if search_term not in actual_name.lower():
            continue

        if actual_name and repo_url:
            results[actual_name] = repo_url

    return results


async def send_results(
    update: Update,
    results,
):
    if not results:
        await update.message.reply_text(
            "❌ Koi match nahi mila."
        )
        return

    text = ""

    for name, url in results.items():
        line = (
            f"📁 {name}\n"
            f"🔗 {url}\n\n"
        )

        if len(text) + len(line) > 3800:
            if text:
                await update.message.reply_text(
                    text,
                    disable_web_page_preview=True,
                )

            text = ""

        text += line

    if text:
        await update.message.reply_text(
            text,
            disable_web_page_preview=True,
        )


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "🤖 GitHub Finder\n\n"
        "🔒 Exact content:\n"
        "/repo mynk\n\n"
        "📄 Similar filename:\n"
        "/filename bomber.py\n\n"
        "📁 Similar repository name:\n"
        "/advrepo mynk-api"
    )


async def repo_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not context.args:
        await update.message.reply_text(
            "Usage:\n/repo mynk"
        )
        return

    query = " ".join(context.args).strip()

    if not query:
        await update.message.reply_text(
            "Usage:\n/repo mynk"
        )
        return

    status = await update.message.reply_text(
        f"🔎 Exact content search...\n\n"
        f"Query: {query}"
    )

    try:
        results = await asyncio.to_thread(
            search_exact_content,
            query,
        )
    except Exception as error:
        await status.edit_text(
            f"❌ Error:\n{error}"
        )
        return

    if not results:
        await status.edit_text(
            f"❌ Exact match nahi mila.\n\n"
            f"Query: {query}"
        )
        return

    await status.edit_text(
        f"✅ Exact matches: {len(results)}\n\n"
        f"Query: {query}"
    )

    await send_results(update, results)


async def filename_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not context.args:
        await update.message.reply_text(
            "Usage:\n/filename bomber.py"
        )
        return

    filename = " ".join(context.args).strip()

    if not filename:
        await update.message.reply_text(
            "Usage:\n/filename bomber.py"
        )
        return

    status = await update.message.reply_text(
        f"🔎 Filename search...\n\n"
        f"Query: {filename}"
    )

    try:
        results = await asyncio.to_thread(
            search_filename,
            filename,
        )
    except Exception as error:
        await status.edit_text(
            f"❌ Error:\n{error}"
        )
        return

    if not results:
        await status.edit_text(
            f"❌ Similar filename nahi mila.\n\n"
            f"Query: {filename}"
        )
        return

    await status.edit_text(
        f"✅ Filename matches: {len(results)}\n\n"
        f"Query: {filename}"
    )

    await send_results(update, results)


async def advrepo_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not context.args:
        await update.message.reply_text(
            "Usage:\n/advrepo mynk-api"
        )
        return

    name = " ".join(context.args).strip()

    if not name:
        await update.message.reply_text(
            "Usage:\n/advrepo mynk-api"
        )
        return

    status = await update.message.reply_text(
        f"🔎 Repository name search...\n\n"
        f"Query: {name}"
    )

    try:
        results = await asyncio.to_thread(
            search_advrepo,
            name,
        )
    except Exception as error:
        await status.edit_text(
            f"❌ Error:\n{error}"
        )
        return

    if not results:
        await status.edit_text(
            f"❌ Similar repository nahi mila.\n\n"
            f"Query: {name}"
        )
        return

    await status.edit_text(
        f"✅ Repository matches: {len(results)}\n\n"
        f"Query: {name}"
    )

    await send_results(update, results)


def run_bot():
    async def bot_main():
        bot_app = (
            Application.builder()
            .token(BOT_TOKEN)
            .build()
        )

        bot_app.add_handler(
            CommandHandler("start", start)
        )

        bot_app.add_handler(
            CommandHandler("repo", repo_command)
        )

        bot_app.add_handler(
            CommandHandler("filename", filename_command)
        )

        bot_app.add_handler(
            CommandHandler("advrepo", advrepo_command)
        )

        print("🤖 GitHub Finder started...")

        await bot_app.initialize()
        await bot_app.start()

        if bot_app.updater is None:
            raise RuntimeError(
                "Telegram updater is not available"
            )

        await bot_app.updater.start_polling()

        try:
            await asyncio.Event().wait()
        finally:
            print("🛑 Stopping Telegram bot...")

            await bot_app.updater.stop()
            await bot_app.stop()
            await bot_app.shutdown()

    asyncio.run(bot_main())


if __name__ == "__main__":
    bot_thread = threading.Thread(
        target=run_bot,
        daemon=True,
    )

    bot_thread.start()

    port = int(
        os.environ.get("PORT", "8080")
    )

    print(
        f"🌐 Health server running on port {port}"
    )

    web_app.run(
        host="0.0.0.0",
        port=port,
        threaded=True,
    )
