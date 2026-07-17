import os
import sys
import tempfile

# Prevent matplotlib font cache permission error by setting config dir early
os.environ["MPLCONFIGDIR"] = tempfile.gettempdir()

# Ensure imports work from project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import DATABASE_PATH, EXPORTS_DIR, REPORTS_DIR
from database import Database
from scanner import WiFiScanner
import analyzer
import charts
from report_generator import ReportGenerator
from gui import WiFiApp

def main():
    # Ensure directories exist
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    # Initialize components
    db = Database(DATABASE_PATH)
    scanner = WiFiScanner()
    report_gen = ReportGenerator(EXPORTS_DIR, REPORTS_DIR)
    
    # Start Application
    app = WiFiApp(scanner, analyzer, db, report_gen, charts)
    app.mainloop()

if __name__ == "__main__":
    main()
