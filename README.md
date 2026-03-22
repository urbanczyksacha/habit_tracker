# 🌱 Habit Tracker

A habit tracking application built with Python, Streamlit, and SQLite.  
Developed as part of the IU portfolio course **DLBDSOOFPP01 — Object Oriented and Functional Programming with Python**.

**Author:** Urbanczyk Sacha  
**Python:** 3.13  
**GitHub:** https://github.com/urbanczyksacha/habit_tracker

---

## 📋 Features

- Create and manage **daily and weekly habits**
- Organise habits into **categories**
- Track habit completion with a **streak system**
- Visualise your progress with **interactive charts** (Plotly)
- Analyse your productivity with an **analytics module** built using functional programming
- Load **predefined sample data** for testing and demonstration

---

## 🗂️ Project Structure

```
habit_tracker/
├── database/
│   ├── database.py       # SQLite connection context manager + DB initialisation
│   ├── schema.sql        # Database schema
│   ├── seed.py           # Predefined habits and 4 weeks of sample data
│   └── habit_tracker.db  # SQLite database (auto-created)
├── test/
│   ├── conftest.py       # Pytest path configuration
│   └── test_analytics.py # Unit tests for the analytics module
├── analytics.py          # Analytics module (functional programming)
├── crud.py               # Data Access Objects (DAO layer)
├── logic.py              # Service layer (business logic)
├── exception.py          # Custom exceptions
├── ht_app.py             # Streamlit UI
└── requirements.txt      # Python dependencies
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/urbanczyksacha/habit_tracker.git
cd habit_tracker
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

- **Windows:**
```bash
venv\Scripts\activate
```
- **macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Application

### Step 1 — Initialise the database

```bash
python -c "from database.database import init_database; init_database()"
```

### Step 2 — Load sample data (optional but recommended)

Loads 5 predefined habits with 4 weeks of realistic tracking data:

```bash
python database/seed.py
```

To reset the sample data at any time:

```bash
python database/seed.py reset
```

### Step 3 — Launch the app

```bash
streamlit run ht_app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 🧪 Running the Tests

The unit test suite covers the analytics module using an in-memory SQLite database with seed data as test fixtures.

```bash
pytest test/ -v
```

---

## 📊 Analytics Module

The `analytics.py` module implements all data analysis using the **functional programming paradigm** — `filter`, `map`, `lambda`, and `reduce` from `functools`.

Key analytics functions:

| Function | Description |
|---|---|
| `completion_rate` | Overall habit completion rate |
| `daily_completion_rate` | Completion rate for a specific day |
| `weekly_completion_rate` | Completion rate for a specific week |
| `category_completion_rate` | Completion rate grouped by category |
| `longuest_habit_streak` | Longest streak for each habit |
| `longuest_habit_streak_by_habit` | Longest streak for a specific habit |
| `current_daystreak` | Current consecutive day streak |
| `longuest_daystreak` | Longest consecutive day streak overall |
| `productivity_comparaison` | Today vs yesterday productivity |
| `best_productivity_period` | Most productive hours of the day |
| `habit_most_productive_day` | Most productive day of the week per habit |
| `completion_trend` | 7-day rolling average completion trend |

---

## 🗃️ Database Schema

The application uses SQLite with the following tables:

- **Category** — habit categories
- **Habit** — habit definitions with periodicity
- **HabitSchedule** — scheduled days per habit
- **HabitLog** — daily completion logs
- **HabitHistory** — history of deleted habits
- **Settings** — application settings

---

## 🌱 Predefined Sample Habits

| Habit | Category | Schedule |
|---|---|---|
| Morning Run | Health | Mon–Fri |
| Meditation | Health | Daily |
| Read 30 minutes | Productivity | Daily |
| Weekly Review | Productivity | Sunday |
| Cook healthy meal | Lifestyle | Wed & Sat |

Sample data covers **4 weeks** with realistic completion rates, including one intentionally difficult week to simulate real usage patterns.

---

## 📦 Dependencies

Main libraries used:

| Library | Purpose |
|---|---|
| `streamlit` | Web UI framework |
| `plotly` | Interactive charts |
| `pandas` | Data manipulation |
| `numpy` | Numerical utilities |
| `pytest` | Unit testing |
| `sqlite3` | Database (built-in) |

Install all dependencies with:

```bash
pip install -r requirements.txt
```
