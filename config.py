# config.py
"""
config.py
Common files
"""

import os


def get_debug_mode():
    """Determine debug mode from environment variable."""
    return os.getenv("FLASK_DEBUG", "False").lower() in (
        "true",
        "1",
        "t",
    )
