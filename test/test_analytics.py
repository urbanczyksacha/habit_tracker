import pytest
import sqlite3
from datetime import date, timedelta
import analytics
from database.seed import seed_database, reset_seed_data
today_date = date.today()
@pytest.fixture
def conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    with open(".\database\schema.sql", "r") as f:
        conn.executescript(f.read())

    seed_database(conn, date.today())
    yield conn
    conn.close()

@pytest.fixture
def habit_logs(conn):
    from crud import HabitLogDAO
    dao =HabitLogDAO(conn)
    return dao.fetch_all_habits_logs()
@pytest.fixture
def today_logs(conn):
    from crud import HabitLogDAO
    dao = HabitLogDAO(conn)
    return dao.fetch_today_habit_logs()
@pytest.fixture
def habit_logs_per_date(conn, date):
    from crud import HabitLogDAO
    dao = HabitLogDAO(conn)
    return dao.fetch_all_habits_logs_per_date(date)


#test of analytics.py

def test_current_daystreak(habit_logs):
    streak = analytics.current_daystreak(habit_logs, today_date)
    assert isinstance(streak, int)
    assert streak >=0
    assert streak <= 28

def test_current_daystreak_empty():
    streak = analytics.current_daystreak([], today_date)
    assert streak == 0 

def test_longuest_daystreak(habit_logs):
    streak = analytics.longuest_daystreak(habit_logs)
    assert isinstance(streak, int)
    assert streak >=0
    assert streak <=28

def test_longuest_daystreak_empty():
    streak = analytics.longuest_daystreak([])
    assert streak == 0

def test_completion_rate(habit_logs):
    done, not_done, rate = analytics.completion_rate(habit_logs)
    assert done + not_done == len(habit_logs)
    assert 0<=rate<=100
    assert isinstance(done, int)
    assert isinstance(rate, float)

def test_completion_rate_emmty():
    assert analytics.completion_rate([]) == (0,0,0)

def test_daily_completion_rate(habit_logs):
    done, not_done, rate = analytics.daily_completion_rate(habit_logs, today_date)
    assert isinstance(done, int)
    assert isinstance(rate,float)

def test_daily_completion_rate_empty():
    done, not_done, rate = analytics.daily_completion_rate([], today_date)
    assert (done, not_done, rate) == (0, 0, 0)

def test_productivity_comparaison(habit_logs,):
    result = analytics.productivity_comparaison(habit_logs, today_date)
    assert isinstance(result,int)
    assert -100<=result<=100

def test_productivity_comparaison_empty():
    result = analytics.productivity_comparaison([], today_date)
    assert result == 0

def test_best_productivity_period(today_logs):
    activity_per_hour, df = analytics.best_productivity_period(today_logs)
    if activity_per_hour is not None and df is not None:
        import pandas as pd
        assert isinstance(df, pd.DataFrame)
        assert 'hour_range' in df.columns
        assert 'hour' in df.columns

def test_weekly_completion_rate(habit_logs):
    week_start = today_date - timedelta(days= today_date.weekday())
    week_end = week_start - timedelta(weeks= 1)
    done, not_done, rate = analytics.weekly_completion_rate(habit_logs, week_start,week_end)
    assert isinstance(done, int)
    assert 0 <= rate <= 100

def test_weekly_completion_rate_empty():
    week_start = today_date - timedelta(days= today_date.weekday())
    week_end = week_start - timedelta(weeks= 1)
    assert analytics.weekly_completion_rate([], week_start,week_end) == (0,0,0)

def test_longuest_habit_streak(habit_logs):
    result = analytics.longuest_habit_streak(habit_logs)
    assert isinstance(result, dict)
    assert all(isinstance(v, int) and v >=0 for v in result.values())

def test_longuest_habit_streak_empty():
    result = analytics.longuest_habit_streak([])
    assert result == {}

def test_longuest_habit_streak_by_habit(habit_logs):
    result = analytics.longuest_habit_streak_by_habit(habit_logs, "Morning Run")

    assert isinstance(result, int)
def test_longuest_habit_streak_by_habit_empty(habit_logs):
    result = analytics.longuest_habit_streak_by_habit([], "Morning Run")

    assert result==0

def test_longuest_habit_streak_by_habit_empty_name(habit_logs):
    result = analytics.longuest_habit_streak_by_habit(habit_logs, "")

    assert result == 0

def test_habit_completion_rate(habit_logs):
    habit_name = "Morning Run"
    done, not_done, rate = analytics.habit_completion_rate(habit_logs,habit_name)
    morning_run_logs = [log for log in habit_logs if log["habit_name"] == habit_name]

    assert 0<= rate <= 100
    assert done + not_done == len(morning_run_logs)

def test_habit_completion_rate_empty(habit_logs):
    habit_name = "Morning Run"
    assert analytics.habit_completion_rate([],habit_name) == (0,0,0)

def test_habit_completion_rate_empty_name(habit_logs):
    habit_name = ""
    assert analytics.habit_completion_rate(habit_logs,habit_name) == (0,0,0)

def test_category_completion_rate(habit_logs):
    result = analytics.category_completion_rate(habit_logs, today_date)
    import pandas as pd
    assert isinstance(result, pd.DataFrame)
    assert "completion_rate" in result.columns
    assert "category_name" in result.columns
    assert (result["completion_rate"] >= 0).all()
    assert (result["completion_rate"] <= 1).all()

def test_category_completion_rate_global(habit_logs):
    result = analytics.category_completion_rate(habit_logs, None)
    import pandas as pd
    assert isinstance(result, pd.DataFrame)
    assert "completion_rate" in result.columns
    assert "category_name" in result.columns
    assert (result["completion_rate"] >= 0).all()
    assert (result["completion_rate"] <= 1).all()

def test_category_completion_rate_weekly(habit_logs):
    second_date = today_date - timedelta(weeks= 1 )
    result = analytics.category_completion_rate(habit_logs, [second_date, today_date])
    import pandas as pd
    assert isinstance(result, pd.DataFrame)
    assert "completion_rate" in result.columns
    assert "category_name" in result.columns
    assert (result["completion_rate"] >= 0).all()
    assert (result["completion_rate"] <= 1).all()

def test_category_completion_rate_empty():
    result = analytics.category_completion_rate([], None)

    import pandas as pd
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0 