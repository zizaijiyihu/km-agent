"""
Configuration for App API
"""

# Default User


# Upload Configuration
ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'xls'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

# Flask Configuration
DEBUG = True
HOST = "0.0.0.0"
PORT = 5000

