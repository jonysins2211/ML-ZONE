import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

def safe_get_env(key: str, default: str = "") -> str:
    """Safely get environment variable"""
    value = os.getenv(key, default)
    if value is None:
        return default
    return value.strip()

def safe_get_int(key: str, default: int = 0) -> int:
    """Safely get integer environment variable"""
    try:
        value = safe_get_env(key, str(default))
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_get_bool(key: str, default: bool = False) -> bool:
    """Safely get boolean environment variable"""
    value = safe_get_env(key, str(default))
    return value.lower() in ("true", "1", "yes", "on", "y")

def safe_get_list(key: str, default=None) -> list:
    """Safely get comma-separated list environment variable"""
    value = safe_get_env(key, "")
    if not value:
        return list(default) if default else []
    return [item.strip() for item in value.split(",") if item.strip()]

def safe_get_int_list(key: str, default=None) -> list:
    """Safely get comma-separated integer list environment variable"""
    values = safe_get_list(key, default)
    result = []
    for item in values:
        try:
            result.append(int(item))
        except (ValueError, TypeError):
            continue
    return result

def safe_get_json(key: str, default=None) -> dict:
    """Safely get JSON environment variable"""
    value = safe_get_env(key, "")
    if not value:
        return dict(default) if default else {}
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else (dict(default) if default else {})
    except (ValueError, TypeError):
        return dict(default) if default else {}

class ConfigMeta(type):
    """Metaclass that falls back to environment variables for unknown attributes.

    Prevents 'type object Config has no attribute X' crashes at import time.
    If a Config attribute is not explicitly defined, we try os.environ first.
    """

    def __getattr__(cls, name: str):
        # Never intercept dunder/magic lookups (breaks copy/pickle/isinstance)
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(name)

        if name.isupper() and name in os.environ:
            value = os.environ[name].strip()
            logger.warning("Config.%s not defined in Config class - using env var fallback", name)
            setattr(cls, name, value)  # cache for next lookup
            return value

        logger.warning("Config.%s not defined and no env var set - returning None", name)
        setattr(cls, name, None)  # cache so warning shows only once
        return None

class Config(metaclass=ConfigMeta):
    # ============ REQUIRED CONFIG ============
    # Support multiple naming conventions
    BOT_TOKEN = safe_get_env("BOT_TOKEN", safe_get_env("TG_BOT_TOKEN", ""))
    API_ID = safe_get_int("API_ID", safe_get_int("TELEGRAM_API", 0))
    API_HASH = safe_get_env("API_HASH", safe_get_env("TELEGRAM_HASH", ""))
    OWNER_ID = safe_get_int("OWNER_ID", 0)
    DATABASE_URL = safe_get_env("DATABASE_URL", "")
    
    # ============ BOT INFO ============
    BOT_USERNAME = safe_get_env("BOT_USERNAME", "ZxZoneMLB_Bot")
    AUTHOR_NAME = safe_get_env("AUTHOR_NAME", "ZxZone Hub")
    AUTHOR_URL = safe_get_env("AUTHOR_URL", "https://t.me/zxzoneupdates")
    
    # ============ CHANNELS & LINKS ============
    UPDATE_CHANNEL = safe_get_env("UPDATE_CHANNEL", "https://t.me/zxzoneupdates")
    REPO_LINK = safe_get_env("REPO_LINK", "https://github.com/obscure-n8/ZxZone-MLB")
    
    # ============ PATHS ============
    BASE_DIR = Path(__file__).parent.parent
    DOWNLOAD_DIR = str(BASE_DIR / "downloads")
    ENCODE_DIR = str(BASE_DIR / "encode")
    THUMB_DIR = str(BASE_DIR / "thumbnails")
    CONFIG_DIR = str(BASE_DIR / "config")
    SESSION_DIR = str(BASE_DIR / "sessions")
    
    # ============ LIMITS ============
    BOT_MAX_TASKS = safe_get_int("BOT_MAX_TASKS", 50)
    USER_MAX_TASKS = safe_get_int("USER_MAX_TASKS", 3)
    QUEUE_LIMIT = safe_get_int("QUEUE_LIMIT", 20)
    
    # ============ ARIA2 ============
    ARIA2_HOST = safe_get_env("ARIA2_HOST", "http://localhost")
    ARIA2_PORT = safe_get_int("ARIA2_PORT", 6800)
    ARIA2_SECRET = safe_get_env("ARIA2_SECRET", "")
    
    # ============ WEB / MIRROR ============
    BASE_URL = safe_get_env("BASE_URL", "").rstrip("/")
    
    # ============ SUDO / ADMIN ============
    SUDO_USERS = safe_get_int_list("SUDO_USERS", [])
    
    # ============ FORCE SUB ============
    FORCE_SUBSCRIBE = safe_get_env("FORCE_SUBSCRIBE", safe_get_env("FORCE_SUB_CHANNEL", ""))
    
    # ============ FEATURE FLAGS ============
    DISABLE_TORRENTS = safe_get_bool("DISABLE_TORRENTS", False)
    DISABLE_LEECH = safe_get_bool("DISABLE_LEECH", False)
    DISABLE_MIRROR = safe_get_bool("DISABLE_MIRROR", False)
    DISABLE_BULK = safe_get_bool("DISABLE_BULK", False)
    DISABLE_MULTI = safe_get_bool("DISABLE_MULTI", False)
    DISABLE_SEED = safe_get_bool("DISABLE_SEED", False)
    DISABLE_FF_MODE = safe_get_bool("DISABLE_FF_MODE", False)
    DISABLE_JD = safe_get_bool("DISABLE_JD", False)
    DISABLE_NZB = safe_get_bool("DISABLE_NZB", False)
    DISABLE_RSS = safe_get_bool("DISABLE_RSS", False)
    DISABLE_SEARCH = safe_get_bool("DISABLE_SEARCH", False)
    DISABLE_STREAM = safe_get_bool("DISABLE_STREAM", False)
    DISABLE_YTDLP = safe_get_bool("DISABLE_YTDLP", False)
    DISABLE_MEGA = safe_get_bool("DISABLE_MEGA", False)
    
    # ============ DOWNLOAD LIMITS (size strings, e.g. "2GB"; empty = unlimited) ============
    DIRECT_LIMIT = safe_get_env("DIRECT_LIMIT", "")
    MEGA_LIMIT = safe_get_env("MEGA_LIMIT", "")
    TORRENT_LIMIT = safe_get_env("TORRENT_LIMIT", "")
    GD_DL_LIMIT = safe_get_env("GD_DL_LIMIT", "")
    RC_DL_LIMIT = safe_get_env("RC_DL_LIMIT", "")
    CLONE_LIMIT = safe_get_env("CLONE_LIMIT", "")
    JD_LIMIT = safe_get_env("JD_LIMIT", "")
    NZB_LIMIT = safe_get_env("NZB_LIMIT", "")
    YTDLP_LIMIT = safe_get_env("YTDLP_LIMIT", "")
    PLAYLIST_LIMIT = safe_get_env("PLAYLIST_LIMIT", "")
    LEECH_LIMIT = safe_get_env("LEECH_LIMIT", "")
    EXTRACT_LIMIT = safe_get_env("EXTRACT_LIMIT", "")
    ARCHIVE_LIMIT = safe_get_env("ARCHIVE_LIMIT", "")
    STORAGE_LIMIT = safe_get_env("STORAGE_LIMIT", "")
    
    # ============ QUEUE ============
    QUEUE_ALL = safe_get_int("QUEUE_ALL", 0)
    QUEUE_DOWNLOAD = safe_get_int("QUEUE_DOWNLOAD", 0)
    QUEUE_UPLOAD = safe_get_int("QUEUE_UPLOAD", 0)
    
    # ============ TASK LIMITS ============
    MAX_TASKS_PER_USER = safe_get_int("MAX_TASKS_PER_USER", USER_MAX_TASKS)
    MAX_TOTAL_TASKS = safe_get_int("MAX_TOTAL_TASKS", BOT_MAX_TASKS)
    
    # ============ LEECH ============
    LEECH_SPLIT_SIZE = safe_get_int("LEECH_SPLIT_SIZE", 2097152000)
    LEECH_DUMP_CHAT = safe_get_int("LEECH_DUMP_CHAT", 0)
    
    # ============ VIDEO ============
    MAX_VIDEO_HEIGHT = safe_get_int("MAX_VIDEO_HEIGHT", 2160)
    
    # ============ SEARCH ============
    SEARCH_API_LINK = safe_get_env("SEARCH_API_LINK", "")
    SEARCH_LIMIT = safe_get_int("SEARCH_LIMIT", 10)
    USE_IMAGES = safe_get_bool("USE_IMAGES", False)
    
    # ============ YTDLP ============
    YTDLP_OPTIONS = safe_get_json("YTDLP_OPTIONS", {})
    
    # ============ UPSTREAM UPDATE ============
    UPSTREAM_REPO = safe_get_env("UPSTREAM_REPO", REPO_LINK)
    UPSTREAM_BRANCH = safe_get_env("UPSTREAM_BRANCH", "main")
    
    # ============ PREMIUM HOSTS ============
    MEGA_EMAIL = safe_get_env("MEGA_EMAIL", "")
    MEGA_PASSWORD = safe_get_env("MEGA_PASSWORD", "")
    JD_EMAIL = safe_get_env("JD_EMAIL", "")
    JD_PASS = safe_get_env("JD_PASS", "")
    ALLDEBRID_API_KEY = safe_get_env("ALLDEBRID_API_KEY", "")
    FILELION_API = safe_get_env("FILELION_API", "")
    STREAMWISH_API = safe_get_env("STREAMWISH_API", "")
    
    # ============ RCLONE ============
    RCLONE_CONFIG = safe_get_env("RCLONE_CONFIG_PATH", str(BASE_DIR / "config" / "rclone.conf"))
    RCLONE_REMOTE = safe_get_env("RCLONE_REMOTE", "gdrive")
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        errors = []
        
        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN/TG_BOT_TOKEN is missing!")
        if not cls.API_ID or cls.API_ID == 0:
            errors.append("API_ID/TELEGRAM_API is missing!")
        if not cls.API_HASH:
            errors.append("API_HASH/TELEGRAM_HASH is missing!")
        if not cls.OWNER_ID or cls.OWNER_ID == 0:
            errors.append("OWNER_ID is missing!")
        if not cls.DATABASE_URL:
            errors.append("DATABASE_URL is missing!")
            
        if errors:
            error_msg = "\n".join(errors)
            print(f"Configuration Error:\n{error_msg}")
            # Don't raise error, just warn
            # Bot will show error message instead of crashing
            return False
            
        return True
    
    @classmethod
    def ensure_dirs(cls):
        """Create necessary directories"""
        dirs = [
            cls.DOWNLOAD_DIR,
            cls.ENCODE_DIR,
            cls.THUMB_DIR,
            cls.CONFIG_DIR,
            cls.SESSION_DIR,
            os.path.join(cls.DOWNLOAD_DIR, "temp"),
            os.path.join(cls.DOWNLOAD_DIR, "queue"),
            os.path.join(cls.DOWNLOAD_DIR, "completed"),
            os.path.join(cls.THUMB_DIR, "users"),
            os.path.join(cls.THUMB_DIR, "watermarks"),
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
