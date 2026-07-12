import os

# ===== ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ (берутся из .env или Render) =====
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "6962118681").split(",")]
API_ID = int(os.environ.get("API_ID", 2040))
API_HASH = os.environ.get("API_HASH", "b18441a1ff607e10a989891a5462e627")

# ===== НАСТРОЙКИ =====
DEFAULT_DELAY = 3
DEFAULT_ONLY_MUTUAL = True
DEFAULT_DELETE_AFTER_SEND = True
DEFAULT_AUTO_DELETE_INVALID = True

# ===== ПУТИ =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SESSIONS_DIR = os.path.join(DATA_DIR, "sessions")
TDATA_DIR = os.path.join(DATA_DIR, "tdatas")
MEDIA_DIR = os.path.join(DATA_DIR, "media")
DB_PATH = os.path.join(DATA_DIR, "duck_spam.db")

for dir_path in [DATA_DIR, SESSIONS_DIR, TDATA_DIR, MEDIA_DIR]:
    os.makedirs(dir_path, exist_ok=True)