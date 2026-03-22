"""
seed.py - Seed data for the Habit Tracker app.

Provides 5 predefined habits (4 daily, 1 weekly) with 4 weeks of
realistic tracking data ending at today's date.

Usage:
    from seed import seed_database, reset_seed_data
    from database.database import db_conn

    with db_conn() as conn:
        seed_database(conn)

    # To reset seed data:
    with db_conn() as conn:
        reset_seed_data(conn)
"""

from datetime import date, timedelta, datetime
import random
import sqlite3


# ---------------------------------------------------------------------------
# Seed definitions
# ---------------------------------------------------------------------------

CATEGORIES = [
    {"name": "Health",       "description": "Physical and mental well-being"},
    {"name": "Productivity", "description": "Work and learning habits"},
    {"name": "Lifestyle",    "description": "Daily life and personal growth"},
]

HABITS = [
    {
        "name":        "Morning Run",
        "description": "Run at least 20 minutes in the morning",
        "category":    "Health",
        "days":        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        # completion probability per week (week 3 is intentionally low)
        "rates":       [0.9, 0.85, 0.4, 0.8],
    },
    {
        "name":        "Meditation",
        "description": "10 minutes of mindfulness meditation",
        "category":    "Health",
        "days":        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "rates":       [0.95, 0.9, 0.5, 0.85],
    },
    {
        "name":        "Read 30 minutes",
        "description": "Read a book or article for at least 30 minutes",
        "category":    "Productivity",
        "days":        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "rates":       [0.8, 0.75, 0.45, 0.9],
    },
    {
        "name":        "Weekly Review",
        "description": "Review goals and plan the upcoming week",
        "category":    "Productivity",
        "days":        ["Sunday"],
        "rates":       [1.0, 1.0, 0.0, 1.0],
    },
    {
        "name":        "Cook healthy meal",
        "description": "Prepare a nutritious home-cooked meal",
        "category":    "Lifestyle",
        "days":        ["Wednesday", "Saturday"],
        "rates":       [0.85, 0.8, 0.5, 0.75],
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_week_dates(end_date: date):
    """Return list of 4 week start dates, oldest first, ending at end_date's week."""
    # Find Monday of end_date's week
    week_end_monday = end_date - timedelta(days=end_date.weekday())
    weeks = []
    for i in range(3, -1, -1):
        weeks.append(week_end_monday - timedelta(weeks=i))
    return weeks  # list of 4 Mondays


def _random_hour():
    """Return a realistic completion timestamp string."""
    hour = random.choices(
        [7, 8, 9, 12, 17, 18, 19, 20, 21],
        weights=[10, 15, 10, 10, 15, 15, 10, 10, 5]
    )[0]
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}:{second:02d}"


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def seed_database(conn, end_date: date = None):
    """
    Insert seed categories, habits, schedules, and 4 weeks of habit logs.

    Args:
        conn: SQLite connection object.
        end_date (date, optional): Last date of the seed period. Defaults to today.

    Example:
        >>> with db_conn() as conn:
        ...     seed_database(conn)
    """
    if end_date is None:
        end_date = date.today()

    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # ---- Categories ----
    category_ids = {}
    for cat in CATEGORIES:
        cursor.execute(
            "INSERT OR IGNORE INTO Category (name, description) VALUES (?, ?)",
            (cat["name"], cat["description"])
        )
        cursor.execute("SELECT id FROM Category WHERE name = ?", (cat["name"],))
        row = cursor.fetchone()
        category_ids[cat["name"]] = row[0]

    conn.commit()

    # ---- Habits + Schedules ----
    habit_ids = {}
    week_starts = _get_week_dates(end_date)
    seed_start = week_starts[0]  # first Monday of the 4-week window

    for habit in HABITS:
        cat_id = category_ids[habit["category"]]
        cursor.execute(
            "INSERT INTO Habit (name, description, category_id, is_seed) VALUES (?, ?, ?, 1)",
            (habit["name"], habit["description"], cat_id)
        )
        habit_id = cursor.lastrowid
        habit_ids[habit["name"]] = habit_id

        # Save creation date as start of seed period
        cursor.execute(
            "UPDATE Habit SET create_at = ? WHERE id = ?",
            (seed_start.isoformat(), habit_id)
        )

        # Schedule
        for day in habit["days"]:
            cursor.execute(
                "INSERT OR IGNORE INTO HabitSchedule (habit_id, day_of_the_week) VALUES (?, ?)",
                (habit_id, day)
            )

        # HabitHistory
        cursor.execute(
            "INSERT INTO HabitHistory (habit_id, name, description, category_id, create_at) VALUES (?, ?, ?, ?, ?)",
            (habit_id, habit["name"], habit["description"], cat_id, seed_start.isoformat())
        )

    conn.commit()

    # ---- HabitLogs ----
    for habit in HABITS:
        habit_id = habit_ids[habit["name"]]
        scheduled_days = habit["days"]

        for week_index, week_start in enumerate(week_starts):
            rate = habit["rates"][week_index]

            for day_offset in range(7):
                current_date = week_start + timedelta(days=day_offset)

                # Don't seed future dates
                if current_date > end_date:
                    break

                day_name = current_date.strftime("%A")
                if day_name not in scheduled_days:
                    continue

                # Decide done or not
                done = 1 if random.random() < rate else 0
                complete_at = None
                if done:
                    time_str = _random_hour()
                    complete_at = f"{current_date.isoformat()} {time_str}"

                cursor.execute(
                    "INSERT OR IGNORE INTO HabitLog (habit_id, done, complete_at, date) VALUES (?, ?, ?, ?)",
                    (habit_id, done, complete_at, current_date.isoformat())
                )

    conn.commit()
    print(f"✅ Seed data inserted — {len(HABITS)} habits, 4 weeks up to {end_date}")


def reset_seed_data(conn):
    """
    Remove all seed habits and their associated logs/schedules.

    Deletes only rows where is_seed = 1 in the Habit table,
    and cascades to HabitLog and HabitSchedule.

    Args:
        conn: SQLite connection object.

    Example:
        >>> with db_conn() as conn:
        ...     reset_seed_data(conn)
    """
    cursor = conn.cursor()

    # Get seed habit ids
    cursor.execute("SELECT id FROM Habit WHERE is_seed = 1")
    seed_ids = [row[0] for row in cursor.fetchall()]

    if not seed_ids:
        print("No seed data found.")
        return

    placeholders = ",".join("?" * len(seed_ids))

    cursor.execute(f"DELETE FROM HabitLog      WHERE habit_id IN ({placeholders})", seed_ids)
    cursor.execute(f"DELETE FROM HabitSchedule WHERE habit_id IN ({placeholders})", seed_ids)
    cursor.execute(f"DELETE FROM HabitHistory  WHERE habit_id IN ({placeholders})", seed_ids)
    cursor.execute(f"DELETE FROM Habit         WHERE id        IN ({placeholders})", seed_ids)

    conn.commit()
    print(f"🗑️  Seed data removed — {len(seed_ids)} habits deleted")


# ---------------------------------------------------------------------------
# CLI usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    from database.database import db_conn

    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        with db_conn() as conn:
            reset_seed_data(conn)
    else:
        with db_conn() as conn:
            seed_database(conn)
