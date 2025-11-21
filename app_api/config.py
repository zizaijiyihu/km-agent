"""
Configuration for App API
"""

# Default User
DEFAULT_USER = "hu"

# Upload Configuration
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

# Flask Configuration
DEBUG = True
HOST = "0.0.0.0"
PORT = 5000
