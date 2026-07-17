import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(PROJECT_ROOT, 'database', 'wifi_analyzer.db')
REPORTS_DIR = os.path.join(PROJECT_ROOT, 'reports')
EXPORTS_DIR = os.path.join(PROJECT_ROOT, 'exports')

# GUI Settings
DEFAULT_THEME = "dark"
APP_TITLE = "WiFi Security Analyzer"
APP_GEOMETRY = "1200x800"

# Refresh Intervals
DEFAULT_REFRESH_INTERVAL = 30  # seconds
