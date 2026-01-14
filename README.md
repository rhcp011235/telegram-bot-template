# Telegram Bot Template (Python)

This repository provides a clean, beginner-friendly Telegram bot template written in Python.
It is designed to be secure, understandable, and easily extensible.

The template includes:
- A basic command structure
- Role-based access control (NORMAL, VIP, ADMIN)
- A hard-coded owner account
- SQLite database for user management
- Environment variable support using a `.env` file
- Safe defaults for GitHub (no secrets committed)

This project is intended to serve as a starting point for custom Telegram bots.

---

## Features

- Python-based Telegram bot using `python-telegram-bot`
- `/start` command with sample commands
- Public commands and restricted admin/owner commands
- SQLite database for persistent user storage
- User roles: NORMAL, VIP, ADMIN
- Hard-coded owner ID for ultimate control
- Secure configuration via `.env`
- Clean GitHub setup with proper `.gitignore`

---

## Project Structure

```
telegram-bot-template/
├── bot.py              # Main bot entry point
├── db.py               # Database logic and helpers
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment configuration
├── .gitignore          # Git ignore rules
├── data/
│   └── .gitkeep        # Keeps the data directory in git
```

---

## Requirements

- Python 3.10 or newer
- A Telegram bot token (from BotFather)
- Git (optional, but recommended)

---

## Step 1: Create a Telegram Bot

1. Open Telegram
2. Search for `@BotFather`
3. Run `/start`
4. Run `/newbot`
5. Choose a name and username
6. Copy the bot token provided

You will need this token in the next steps.

---

## Step 2: Clone the Repository

```bash
git clone git@github.com:rhcp011235/telegram-bot-template.git
cd telegram-bot-template
```

---

## Step 3: Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

---

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 5: Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env`:

```env
BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
DB_PATH="./data/bot.db"
LOG_LEVEL="INFO"
```

Important:
- Never commit `.env` to GitHub
- `.env` is ignored automatically via `.gitignore`

---

## Step 6: Set the Bot Owner

Open `bot.py` and locate:

```python
OWNER_TELEGRAM_ID = 123456789
```

Replace this value with your numeric Telegram user ID.

You can obtain your ID by messaging `@userinfobot` on Telegram.

---

## Step 7: Run the Bot

```bash
python bot.py
```

If successful, logging output will indicate the bot has started.

---

## Available Commands

### Public Commands

- `/start`
- `/example1`
- `/example2`
- `/example3`
- `/whoami`

### Admin and Owner Commands

- `/users`
- `/setrole <telegram_id> <NORMAL|VIP|ADMIN>`

Users must run `/start` at least once before their role can be modified.

---

## User Roles Explained

| Role   | Description |
|--------|-------------|
| NORMAL | Default role for all users |
| VIP    | Reserved for premium or trusted users |
| ADMIN  | Administrative access |
| OWNER  | Hard-coded full control |

---

## Database Details

- SQLite database created automatically on startup
- Configurable location via `.env`
- No manual schema setup required

---

## Security Notes

- Secrets are stored in `.env`
- Database files are ignored by Git
- Owner privileges cannot be overridden

---

## Extending the Bot

You can extend this template by:
- Adding inline keyboards
- Adding VIP-only commands
- Adding webhook support
- Adding Docker support

---

## License

Provided as-is for educational and development purposes.
