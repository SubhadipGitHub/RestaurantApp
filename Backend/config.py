"""Environment configuration with fail-fast validation.

Importing this module raises a clear, actionable error when a required
variable is missing, instead of letting the app die on an opaque TypeError
deep inside a URL-encoding call at import time.
"""

import os
import urllib.parse

from dotenv import load_dotenv

load_dotenv()


class ConfigError(RuntimeError):
    """Raised when the process is missing configuration it cannot run without."""


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ConfigError(
            f"Required environment variable {name} is not set. "
            f"See Backend/.env.example for the full list."
        )
    return value


def _flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


# --- MongoDB ---------------------------------------------------------------
# Preferred: paste the connection string straight from Atlas's "Connect" dialog.
# Falls back to assembling it from parts for compatibility with the older setup.
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "restoDB")

_mongo_uri = os.getenv("MONGO_URI")
if _mongo_uri:
    MONGO_DB_URL = _mongo_uri
else:
    MONGO_USERNAME = _require("MONGO_USERNAME")
    MONGO_PASSWORD = _require("MONGO_PASSWORD")
    MONGO_CLUSTER_URL = _require("MONGO_CLUSTER_URL")
    MONGO_DB_URL = (
        f"mongodb+srv://{urllib.parse.quote_plus(MONGO_USERNAME)}:"
        f"{urllib.parse.quote_plus(MONGO_PASSWORD)}@{MONGO_CLUSTER_URL}/"
        f"{MONGO_DB_NAME}?retryWrites=true&w=majority"
    )

# --- Google OAuth ----------------------------------------------------------
GOOGLE_CLIENT_ID = _require("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = _require("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = _require("GOOGLE_CLIENT_REDIRECT")

# --- Session ---------------------------------------------------------------
# Signing key for our OWN session tokens. Deliberately not the Google client
# secret: that is rotatable out-of-band by Google and would silently invalidate
# every session.
SECRET_KEY = _require("SECRET_KEY")
JWT_ALGORITHM = "HS256"
SESSION_COOKIE_NAME = "session"
SESSION_TTL_SECONDS = 60 * 60 * 24 * 7  # 7 days

# Set to false only for local http development.
COOKIE_SECURE = _flag("COOKIE_SECURE", True)

# --- Frontend --------------------------------------------------------------
FRONTEND_URL = _require("FRONTEND_URL").rstrip("/")

# --- Misc ------------------------------------------------------------------
# The API documents every mutation endpoint, so it stays off unless asked for.
ENABLE_DOCS = _flag("ENABLE_DOCS", False)
PORT = int(os.getenv("PORT", "8000"))
