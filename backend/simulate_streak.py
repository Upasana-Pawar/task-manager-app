# simulate_streak.py (place in backend/)
from datetime import date, timedelta, datetime
import os
from backend import db, Habit  # if your structure imports like this; otherwise use sqlalchemy to open file directly

# Simple raw sqlite approach (no imports):
import sqlite3
DB = os.path.join(os.path.dirname(__file__), "data.db")
conn = sqlite3.connect(DB)
cur = conn.cursor()

hid = 1  # change to your habit id
# set last_completed to 6 days ago and streak to 6, then call /habits/1/complete once
six_days_ago = (date.today() - timedelta(days=6)).isoformat()
cur.execute("UPDATE habit SET last_completed = ?, streak = ? WHERE id = ?", (six_days_ago, 6, hid))
conn.commit()
conn.close()
print("Simulated habit streak base: last_completed =", six_days_ago, "streak set to 6")
