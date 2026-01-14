import os
import logging
from dotenv import load_dotenv

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from db import Database, VALID_ROLES

# ----------------------------
# HARD-CODED OWNER (required)
# Put your Telegram numeric user ID here.
# You can get it by messaging @userinfobot in Telegram.
# ----------------------------
OWNER_TELEGRAM_ID = 123456789  # <-- CHANGE THIS

# Role precedence
ROLE_RANK = {"NORMAL": 1, "VIP": 2, "ADMIN": 3}


def is_owner(user_id: int) -> bool:
    return user_id == OWNER_TELEGRAM_ID


def has_min_role(user_role: str | None, required: str) -> bool:
    if not user_role:
        return False
    return ROLE_RANK.get(user_role, 0) >= ROLE_RANK.get(required, 999)


def require_owner(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id if update.effective_user else 0
        if not is_owner(uid):
            await update.message.reply_text("🚫 Owner-only command.")
            return
        return await func(update, context)
    return wrapper


def require_admin_or_owner(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id if update.effective_user else 0
        db: Database = context.application.bot_data["db"]
        role = db.get_user_role(uid)

        if is_owner(uid) or has_min_role(role, "ADMIN"):
            return await func(update, context)

        await update.message.reply_text("🚫 Admin-only command.")
    return wrapper


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db: Database = context.application.bot_data["db"]

    u = update.effective_user
    if not u:
        return

    db.ensure_user_exists(u.id, u.username, u.first_name)

    text = (
        "<b>Bot Template</b>\n\n"
        "Available commands:\n"
        "• /example1\n"
        "• /example2\n"
        "• /example3\n\n"
        "Admin/Owner commands:\n"
        "• /whoami\n"
        "• /users\n"
        "• /setrole <telegram_id> <NORMAL|VIP|ADMIN>\n"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db: Database = context.application.bot_data["db"]
    u = update.effective_user
    if not u:
        return

    db.ensure_user_exists(u.id, u.username, u.first_name)
    role = db.get_user_role(u.id) or "UNKNOWN"

    owner_flag = "YES" if is_owner(u.id) else "NO"
    text = (
        f"<b>Your Info</b>\n"
        f"• ID: <code>{u.id}</code>\n"
        f"• Username: @{u.username if u.username else 'N/A'}\n"
        f"• Role: <b>{role}</b>\n"
        f"• Owner: <b>{owner_flag}</b>\n"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def example1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Example1 response: basic public command.")


async def example2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Example2 response: basic public command.")


async def example3(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Example3 response: basic public command.")


@require_admin_or_owner
async def users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db: Database = context.application.bot_data["db"]
    rows = db.list_users(limit=50)

    if not rows:
        await update.message.reply_text("No users found.")
        return

    lines = ["<b>Latest users (up to 50)</b>"]
    for tid, role, username in rows:
        uname = f"@{username}" if username else "N/A"
        lines.append(f"• <code>{tid}</code> — <b>{role}</b> — {uname}")

    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


@require_owner
async def setrole(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Owner-only:
      /setrole <telegram_id> <NORMAL|VIP|ADMIN>
    """
    db: Database = context.application.bot_data["db"]

    if not context.args or len(context.args) != 2:
        await update.message.reply_text("Usage: /setrole <telegram_id> <NORMAL|VIP|ADMIN>")
        return

    try:
        telegram_id = int(context.args[0])
        role = context.args[1].upper().strip()
        if role not in VALID_ROLES:
            raise ValueError()
    except Exception:
        await update.message.reply_text("Invalid args. Example: /setrole 123456789 VIP")
        return

    # Ensure the target exists in DB (optional, but helpful)
    # We don't know username/first_name for arbitrary users, so we just update role if row exists.
    updated = db.set_role(telegram_id, role)
    if not updated:
        await update.message.reply_text(
            "User not found in DB yet. Have them press /start first, then retry."
        )
        return

    await update.message.reply_text(f"✅ Set <code>{telegram_id}</code> role to <b>{role}</b>.", parse_mode=ParseMode.HTML)


def main() -> None:
    load_dotenv()

    bot_token = os.getenv("BOT_TOKEN", "").strip()
    db_path = os.getenv("DB_PATH", "./data/bot.db").strip()
    log_level = os.getenv("LOG_LEVEL", "INFO").upper().strip()

    if not bot_token:
        raise SystemExit("Missing BOT_TOKEN in .env")

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    logging.basicConfig(
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        level=getattr(logging, log_level, logging.INFO),
    )

    db = Database(db_path)

    app = Application.builder().token(bot_token).build()
    app.bot_data["db"] = db

    # Public
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("whoami", whoami))
    app.add_handler(CommandHandler("example1", example1))
    app.add_handler(CommandHandler("example2", example2))
    app.add_handler(CommandHandler("example3", example3))

    # Admin/Owner
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("setrole", setrole))

    logging.getLogger(__name__).info("Bot started.")
    app.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
