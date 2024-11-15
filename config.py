# config.py
"""
config.py
Common files
"""

import os
import secrets

SECRET_KEY = secrets.token_hex(32)

import os

# Base URL for CAS
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
CAS_SERVER = "https://cas.princeton.edu"
CAS_LOGIN_ROUTE = f"{CAS_SERVER}/login"
CAS_LOGOUT_ROUTE = f"{CAS_SERVER}/logout"
CAS_VALIDATE_ROUTE = f"{CAS_SERVER}/validate"
CAS_SERVICE = f"{BASE_URL}/auth/cas"

def get_debug_mode():
    """Determine debug mode from environment variable."""
    return os.getenv("FLASK_DEBUG", "False").lower() in (
        "true",
        "1",
        "t",
    )
