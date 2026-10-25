import os
import sys
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

try:
    xkq_admin_root = int(os.getenv("xkq_admin_root", "8797858167").strip())
except ValueError:
    print("⚠️ WARNING: Invalid xkq_admin_root. Using 8797858167.")
    xkq_admin_root = 8797858167

MAX_REJECT = 3
DB_NAME = os.getenv("DB_NAME", "bot_database.db").strip() or "bot_database.db"

if not BOT_TOKEN:
    print("❌ FATAL ERROR: BOT_TOKEN environment variable is not set or empty!")
    sys.exit(1)

                                                                           
ADMINS = [xkq_admin_root]
