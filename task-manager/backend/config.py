# config.py — SQLite Configuration
# The database is a single file stored in the backend folder.
# No server, no password, no setup needed!

import os

# Path to the SQLite database file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "task_manager.db")
