This is a **Python habit tracking app** that helps users keep track of daily or weekly habits, see their progress, and stay motivated. The app also provides simple analytics and a rewards system for reaching streak milestones.

---

## Features

* Add, modify, or delete habits, either daily or weekly.
* Assign habits to categories.
* Mark habits as done or undone, with automatic streak tracking.
* View analytics:

  * Most completed habits
  * Most productive days
  * Habit completion by category
  * Longest streaks
* Rewards based on streak milestones (5, 15, 25, 50 days).
* Motivational messages displayed daily.

---

## How to Set Up

1. Clone the project:

```bash
git clone https://github.com/your-username/habit-tracker.git
cd habit-tracker
```

2. (Optional) Create a virtual environment:

```bash
python -m venv venv
# Activate it
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
streamlit run habit_tracker_app.py
```

**Required packages:** `streamlit`, `pandas`, `numpy`, `plotly`

---

## Project Structure

```
habit-tracker/
│
├── habit_tracker_app.py                  # Main Streamlit interface
├── habit_tracker.py        # Backend: Habit, Category, Stat classes
├── database.db             # SQLite database (created automatically)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

**Main classes:**

* `Habit` – handles adding, editing, deleting habits, and marking them done
* `Category` – manages habit categories
* `Stat` – calculates statistics and generates charts

---

## How to Use

* **Home Tab:** see today’s habits, mark them done, view streaks and motivational messages.
* **Habits Tab:** add, edit, delete habits; check weekly agenda.
* **Category Tab:** manage habit categories.
* **Analyse Habit Tab:** see charts for habits completed, streaks, and category performance.
* **Reward Tab:** check reward milestones for streaks.

---

## Notes

* Uses **SQLite** for storage.
* The UI is built with **Streamlit** for an interactive experience.
* **Plotly** is used for charts.
* Object-oriented programming is applied for modularity.
* Functional programming is used for statistics and aggregations.


---