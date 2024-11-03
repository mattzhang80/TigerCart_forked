# config.py
"""
config.py
Common files
"""

import os
import secrets

SECRET_KEY = secrets.token_hex(32)


def get_debug_mode():
    """Determine debug mode from environment variable."""
    return os.getenv("FLASK_DEBUG", "False").lower() in (
        "true",
        "1",
        "t",
    )
