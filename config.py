"""UniTK Application Configuration."""

import os
from pathlib import Path

APP_NAME = "Bokmål"
APP_VERSION = "0.1.0"
APP_TITLE = f"{APP_NAME} - Project Manager"

# Database
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "data"
DB_PATH.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{DB_PATH / 'bokmal.db'}"

# Calendar defaults
DEFAULT_WORKING_DAYS = [0, 1, 2, 3, 4]  # Mon-Fri
DEFAULT_WORKING_HOURS_START = 9
DEFAULT_WORKING_HOURS_END = 17
DEFAULT_HOURS_PER_DAY = 8

# Gantt chart defaults
GANTT_ROW_HEIGHT = 32
GANTT_HEADER_HEIGHT = 50
GANTT_MIN_COL_WIDTH = 30
GANTT_DAY_WIDTH = 40
GANTT_WEEK_WIDTH = 20
GANTT_MONTH_WIDTH = 6

# UI
SPLITTER_DEFAULT_RATIO = [400, 600]
