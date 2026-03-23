import pytest
import sqlite3
from database.seed import seed_database
from datetime import datetime, timedelta
from crud import HabitDAO



@pytest.fixture
def conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    with open(r".\database\schema.sql", "r") as f:
        conn.executescript(f.read())


    yield conn
    conn.close()



def test_add_habit(conn,):
    from crud import HabitDAO, CategoryDAO
    from logic import HabitService
    habit_dao = HabitDAO(conn)
    category_dao = CategoryDAO(conn)
    habit_service = HabitService(habit_dao)

    category_dao.add_category("Test Cat", "Testing")

    habit_service.add_habit("Test habit", "test", 1, ['Monday', 'Tuesday', 'Friday'])
    
    habits = habit_dao.fetch_habit()
    assert habits is not None
    if habits:
        names = [dict(h)["name"] for h in habits]
        assert "Test habit" in names




def test_update_habit(conn):
    from crud import HabitDAO, CategoryDAO
    from logic import HabitService
    habit_dao = HabitDAO(conn)
    category_dao = CategoryDAO(conn)
    habit_service = HabitService(habit_dao)

    category_dao.add_category("Test Cat", "Testing")
    category_dao.add_category("Test Cat 2", "Testing 2")

    habit_service.add_habit("Test habit", "test", 1, ['Monday', 'Tuesday', 'Friday'])
    habit_service.update_habit("HABIT TEST","TEST UPDATE", 2,  1, ['Monday','Friday'])
    habits = habit_dao.fetch_habit()
    if habits:
        names = [dict(h)["name"] for h in habits]
        categories = [dict(h)["category_name"] for h in habits]
        desc = [dict(h)["description"] for h in habits]
        assert "HABIT TEST" in names
        assert "Test Cat 2" in categories
        assert "TEST UPDATE" in desc

def test_delete_habit(conn):
    from crud import HabitDAO, CategoryDAO
    from logic import HabitService
    habit_dao = HabitDAO(conn)
    category_dao = CategoryDAO(conn)
    habit_service = HabitService(habit_dao)

    category_dao.add_category("Test Cat", "Testing")

    habit_service.add_habit("Test habit", "test", 1, ['Monday', 'Tuesday', 'Friday'])
    habit_service.delete_habit(1)
    result = habit_dao.fetch_habit()

    assert result is None or result == [] or len(result) == 0