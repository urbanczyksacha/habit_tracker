#Habit tracker with hbait class,
#importing library that I need
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
from datetime import timedelta
from exception import DatabaseError
import numpy as np
from database.database import db_conn

class BaseDAO:
    """
    Base Data Access Object providing a centralized query execution method.

    All DAO classes inherit from BaseDAO to share a single, consistent
    interface for executing SQLite queries with error handling.

    Args:
        conn: An active SQLite connection object.

    Example:
        >>> class MyDAO(BaseDAO):
        ...     def fetch(self):
        ...         return self.execute("SELECT * FROM MyTable", fetch="all")
    """
    def __init__(self,conn) -> None:
        self.conn = conn
    def execute(self, query, params = None, fetch = None, commit = False):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params or ())
            if commit:
                self.conn.commit()
                return cursor.lastrowid
            if fetch == "one":
                return cursor.fetchone()
            elif fetch == "all":
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[DB ERROR]: {e}")
            raise DatabaseError(f"Database error :{e}")
        
#creating category class to output the predefined category, save new one, deleting category
#The class category is used to have everythings with category action, like deleting, adding, choosing.
class CategoryDAO(BaseDAO) :
    """
    Manages categories of habits stored in the SQLite database.

    Provides static methods to:
      - fetch all categories.
      - Add, update, and delete categories.
      - Validate deletion by checking linked habits.

    Categories help organize habits into groups for better management.

    Usage example:
        >>> Category.add_category("Health", "Physical and mental well-being")
        >>> df = Category.fetch_category()
        >>> Category.update_category("Fitness", "Updated description", "Health")
        >>> Category.delete_category(3)
    """
    def fetch_category(self):
        """
        Collects data from the database to display the list of categories on the UI.

        This function connects to the SQLite database 'habit_tracker.db', selects 
        all categories, and returns them as a DataFrame with the columns:
        'CategoryID', 'Name', and 'Description'.

        Returns:
            pd.DataFrame: A DataFrame containing the category data.

        Raises:
            sqlite3.Error: If there is an issue connecting to or querying the database.

        Example:
            >>> df = ClassName.fetch_category()
            >>> print(df.head())
        """
        #connecting in the data base, selecting and export to a dataframe
        
        result = self.execute("SELECT id AS category_id, name as category_name, description FROM Category", fetch= "all")
        return result
        
    def add_category(self,category_name, category_desc):
        """
        Adds a new category to the database.

        This function inserts a new row into the 'Category' table in the
        SQLite database using the provided category name and description.

        Args:
            category_name (str): The name of the new category.
            category_desc (str): A short description of the category.

        Raises:
            sqlite3.Error: If an error occurs while inserting into the database.

        Example:
            >>> add_category("Health", "Habits related to physical and mental well-being")
        """

        result = self.execute("""INSERT INTO Category (name, description) VALUES (?,?)""", (category_name, category_desc), commit = True)
        return result
    def update_category(self,new_category_name, new_category_desc,category_name):
        """
        Updates an existing category's name and description in the database.

        The function searches for the category by its current name, and if found,
        updates its name and description.

        Args:
            new_category_name (str): The updated name of the category.
            new_category_desc (str): The updated description of the category.
            category_name (str): The current name of the category to update.

        Raises:
            sqlite3.Error: If an error occurs while updating the database.

        Example:
            >>> update_category("Fitness", "Updated description", "Health")
        """
        
            #Uptading the sql row to not recreate a new id and to keep the same category and just update it
        result = self.execute("""UPDATE Category SET name = ? ,description = ? WHERE name = ?""", (new_category_name, new_category_desc, category_name), commit= True)
        return result
    def delete_category(self,category_id):
        """
        Deletes a category from the database by its ID.

        This function removes the category entry from the 'Category' table
        based on the given CategoryID.

        Args:
            category_id (int): The ID of the category to delete.

        Raises:
            sqlite3.Error: If the deletion query fails.

        Example:
            >>> delete_category(3)
        """
            #deleting the entire row where the category ID is
        result = self.execute("DELETE FROM Category WHERE id = ?", (category_id,))
        if result is None:
            return {"error" : "Database error : Impossible to delete a category righ now, please try later."}
        return result
    
    def delete_category_validation(self,category_id):
        """
        Checks whether a category is linked to existing habits.

        This function verifies if the category is associated with any habit in the
        'Habit' table. It returns the number of linked habits, which is useful for
        preventing deletion of categories still in use.

        Args:
            category_id (int): The ID of the category to check.

        Returns:
            int: The number of habits linked to this category.

        Raises:
            sqlite3.Error: If the SELECT query fails.

        Example:
            >>> count = delete_category_validation(2)
            >>> if count == 0:
            ...     delete_category(2)
        """
            #Count the number of habit linked with the category that the user want to delete
        result=  self.execute("SELECT COUNT(*) FROM Habit WHERE category_id = ?", (category_id,), fetch= "one")
        if result is None:
            return {"error" : "Database error : Impossible to call the database righ now, please try later."}
        return result
            


class HabitDAO(BaseDAO):
    """
    Manages habits for tracking daily tasks with persistence in a SQLite database.

    This class provides static methods to:
      - fetch today's habits or all habits with details.
      - Add, delete, and update habits.
      - Mark habits as done or undone.
      - Reset daily 'done' status of all habits.
    
    Habits are stored in the 'Habit' table, associated days in 'HabitSchedule',
    and activity logs in 'HabitLog'. Categories are stored in 'Category' table.
    The 'Settings' table holds metadata like the last reset date.

    Usage example:
        >>> Habit.add_habit()
        >>> todays = Habit.fetch_today_habit()
        >>> Habit.mark_done()
        >>> Habit.reset_done()
    """
    def add_daily_habit_log(self):
        today = datetime.today().strftime('%A')
        today_date = datetime.today().date()
            #selecting the habit of where the Days is today.
        habits = self.execute("""SELECT h.name, h.id
            FROM Habit h
            JOIN HabitSchedule d ON h.id = d.habit_id
            WHERE d.day_of_the_week = ? """, (today,), fetch= "all")
        if habits:
            for habit in habits:
                habit_id = habit["id"]
                habit_name = habit["name"]
                self.execute("INSERT OR IGNORE INTO HabitLog (habit_id,done, date) VALUES (?,?,?)", (habit_id,0,today_date,), commit= True)
    
    def fetch_today_habit(self):
        """
        Returns a list of today's habits based on the current weekday.

        The function fetches all habits that are scheduled for today by joining
        the 'Habit' and 'HabitSchedule' tables using the current weekday (e.g., "Monday").

        Returns:
                list of tuples: Each tuple contains (Name, HabitID, Done) for today's habits.

        Example:
            >>> habits = fetch_today_habit()
            >>> for h in habits:
            ...     print(h)
        """
        today_date = datetime.today().date()
            #selecting the habit of where the Days is today.
        result = self.execute("""SELECT h.id AS habit_id, h.name AS name, hl.done AS done
            FROM HabitLog hl
            JOIN Habit h ON h.id = hl.habit_id
            WHERE hl.date = ? """, (today_date,), fetch= "all")
        if result is None:
            raise DatabaseError("Problem")
        return [dict(row) for row in result]
    def fetch_habit_by_day(self):
            result = self.execute("""SELECT h.name AS name, h.description, c.name as category_name, hs.day_of_the_week as day
                           FROM Habit h
                           JOIN Category c ON h.category_id = c.id 
                           JOIN HabitSchedule hs ON h.id = hs.habit_id""", fetch= "all")
            if result is None:
                return {"error" : "Database error : Impossible to get yours habits righ now, please try later."}
            return result
    def fetch_habit(self):
        """
        fetchs all habits with their details.

        This function joins the Habit, HabitSchedule, and Category tables to return
        detailed information about each habit including its ID, name, associated
        category, days of the week, and creation date.

        Returns:
            pd.DataFrame: Columns are ['HabitID','Habit', 'Category','Days', 'CreateAt'].

        Example:
            >>> df = fetch_habit()
            >>> print(df)
        """
        result = self.execute("""
            SELECT h.id AS habit_id, h.name as name,h.description, c.name AS category_name
            ,GROUP_CONCAT(DISTINCT d.day_of_the_week) AS days, h.create_at
            FROM Habit h
            LEFT JOIN HabitSchedule d ON h.id = d.habit_id
            LEFT JOIN  Category c ON h.category_id= c.id
            GROUP BY h.id, h.name, c.name;
        """, fetch="all")

        return result
    def add_habit(self,habit_name,habit_desc, category_id,days):
        """
        Adds a new habit and assigns it to specific days.

        Inserts a new habit into the 'Habit' table and associates it with selected
        days in the 'HabitSchedule' table.

        Args:
            habit_name (str): The name of the new habit.
            category_id (int): The ID of the associated category.
            days (list of str): Days the habit should be tracked (e.g., ['Monday', 'Wednesday']).

        Raises:
            sqlite3.Error: If an error occurs during insertion.

        Example:
            >>> add_habit("Meditate", 1, ["Monday", "Friday"])
        """
            #Inserting user input habit_name and category-id in the database, the other CreateAt and the HabitID is automated in the sql table
        today_date = datetime.today().date()
        today_weekday= today_date.strftime("%A")
        habit_id = self.execute("INSERT INTO Habit (name, description, category_id) VALUES (?, ?, ?)", (habit_name, habit_desc, category_id), commit= True)
        habit_create_at = self.execute("SELECT create_at FROM Habit WHERE id = (?)", (habit_id,),fetch = "one")
        if habit_create_at:
            result = self.execute("INSERT INTO HabitHistory (habit_id, name, description, category_id, create_at) VALUES (?, ?, ?,?,?)", (habit_id, habit_name, habit_desc, category_id, habit_create_at[0],), commit= True)
            #inserting the habitID with the days choice by the user in the HabitSchedule table one day by one
            for day in days:
                result = self.execute("INSERT INTO HabitSchedule (habit_id, day_of_the_week) VALUES (?, ?)", (habit_id, day), commit= True)
            if today_weekday in days:
                self.execute("INSERT OR IGNORE INTO HabitLog (habit_id,done, date) VALUES (?,?,?)", (habit_id,0,today_date,), commit= True)
            if result is None:
                return {"error" : "Database error : Impossible to add a habit righ now, please try later."}
            return result 


    def delete_habit(self, habit_id):
        """
        Deletes a habit from the database and stores it in history.

        Before deletion, the habit's name and creation date are saved into
        'HabitHistory' for tracking purposes.

        Args:
            habit_id (int): The ID of the habit to delete.

        Raises:
            sqlite3.Error: If the deletion or logging fails.

        Example:
            >>> delete_habit(5)
        """
            #selecting the habit who's gonna be deleted
        result = self.execute("DELETE FROM Habit WHERE id = ?", (habit_id,), commit= True)
        if result is None:
            return {"error" : "Database error : Impossible to delete a habit righ now, please try later."}
        return result

    def update_habit(self, habit_new_name,category_id, habit_id, days):
        """
        Modifies a habit's name, category, and scheduled days.

        This function updates the habit in the database and resets its assigned
        days in 'HabitSchedule' with the new list provided.

        Args:
            habit_new_name (str): New name for the habit.
            category_id (int): Updated category ID.
            habit_id (int): The ID of the habit to update.
            days (list of str): New days for the habit.

        Raises:
            sqlite3.Error: If update operations fail.

        Example:
            >>> update_habit("Workout", 2, 1, ["Tuesday", "Thursday"])
        """
        habit_new_name = habit_new_name.strip()
        if len(habit_new_name) >= 1 :
            result = self.execute("UPDATE Habit SET Name = ? WHERE id = ?", (habit_new_name, habit_id,),commit= True )
        elif category_id is not None:
            result = self.execute("UPDATE Habit SET category_id = ? WHERE id = ?", (category_id, habit_id,), commit= True)
        elif len(days) >= 1:
            result = self.execute("DELETE FROM HabitSchedule WHERE habit_id = ?", (habit_id,), commit= True)
            for day in days:
                result = self.execute("INSERT INTO HabitSchedule VALUES(?,?)", ( habit_id, day,), commit = True)
            return result

    def update_done(self,habit_id, done = None):
        """
        Marks a habit as done for today.

        Adds an entry to the 'HabitLog' table and updates the 'Done' field
        in the 'Habit' table.

        Args:
            habit_id (int): The ID of the habit to mark as done.

        Example:
            >>> mark_done(1)
        """
        today = datetime.today().isoformat(" ", "seconds")
        today_date = datetime.today().date()
        if done == 0 :
            today = None
            #update the status done in the table Habit
        result = self.execute(
                "UPDATE Habitlog SET done = ? ,complete_at = ? WHERE habit_id = ? AND date = ?",
                (done, today,habit_id, today_date,), commit= True)
        if result is None:
            return {"error" : "Database error : Impossible to update done of the habit righ now, please try later."}
        return result

class HabitLogDAO(BaseDAO):
    """
    Manages habit log entries stored in the HabitLog table.

    Provides methods to:
      - Sync missing logs for days where the app was not opened.
      - Fetch all habit logs, filtered by date or habit.
      - Insert daily habit logs for today's scheduled habits.

    HabitLog stores one entry per habit per day, tracking whether
    the habit was completed and at what time.

    Example:
        >>> dao = HabitLogDAO(conn)
        >>> logs = dao.fetch_all_habits_logs()
        >>> dao.sync_missing_logs()
    """
    def get_last_log_date(self):
        row = self.execute("SELECT MAX(date) as last_date FROM HabitLog", fetch= "one")
        return row["last_date"] if row and row["last_date"] else None
    def sync_missing_logs(self):
        """
        Fills in missing HabitLog entries for days the app was not opened.

        Checks the last log date and inserts entries for each day between
        then and today, for all habits scheduled on those days.
        """
        last_date_str = self.get_last_log_date()
        today_date = datetime.today().date()
        if not last_date_str:
            return
        last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
        current = last_date + timedelta(1)

        while current <= today_date:
            day = current.strftime("%A")
            habits = self.execute("""SELECT h.name, h.id
            FROM Habit h
            JOIN HabitSchedule d ON h.id = d.habit_id
            WHERE d.day_of_the_week = ? """, (day,), fetch= "all")
            if habits:
                for habit in habits:
                    habit_id = habit["id"]
                    habit_name = habit["name"]
                    self.execute("INSERT OR IGNORE INTO HabitLog (habit_id,done, date) VALUES (?,?,?)", (habit_id,0,current,), commit= True)
            current += timedelta(1)

    def add_daily_habit_log(self):
        today = datetime.today().strftime('%A')
        today_date = datetime.today().date()
            #selecting the habit of where the Days is today.
        habits = self.execute("""SELECT h.name, h.id
            FROM Habit h
            JOIN HabitSchedule d ON h.id = d.habit_id
            WHERE d.day_of_the_week = ? """, (today,), fetch= "all")
        if habits:
            for habit in habits:
                habit_id = habit["id"]
                habit_name = habit["name"]
                self.execute("INSERT OR IGNORE INTO HabitLog (habit_id,done, date) VALUES (?,?,?)", (habit_id,0,today_date,), commit= True)
    def fetch_all_habits_logs(self):
        """
        Fetches all habit logs with habit and category details.

        Returns:
            list[dict]: Each dict contains habit_name, category_name,
                done, complete_at, and date.
        """
        result = self.execute("""SELECT h.name AS habit_name, c.name AS category_name, done, complete_at,date FROM HabitLog hl
                                JOIN Habit h ON h.id = hl.habit_id
                                JOIN Category c ON c.id = h.category_id""", fetch= "all")
        if result:
            return [dict(row) for row in result]
    def fetch_all_habits_logs_per_date(self,date):
        """
        Fetches habit logs filtered by one or more dates.

        Args:
            date (list): List of date strings in 'YYYY-MM-DD' format.

        Returns:
            list[dict]: Filtered logs or None if no results.
        """
        if len(date) > 1:
            placeholder = ",".join("?"*len(date))
        else:
            placeholder = date
        result = self.execute(f"""SELECT h.name AS habit_name, c.name AS category_name, done, complete_at,date FROM HabitLog hl
                                JOIN Habit h ON h.id = hl.habit_id
                                JOIN Category c ON c.id = h.category_id
                              WHERE hl.date IN ({placeholder})""",tuple(date), fetch= "all")
        if result:
            return [dict(row) for row in result]
        else:
            return None
    def fetch_today_habit_logs(self):
        """
        Fetches habit logs for today only.

        Returns:
            list[dict]: Today's logs with habit_id, habit_name,
                category_name, done, complete_at, and date.
            None if no logs found.
        """
        today_date = datetime.today().date()
        result = self.execute("""SELECT h.id as habit_id,h.name AS habit_name, c.name AS category_name, hl.done, hl.complete_at,hl.date FROM HabitLog hl
                                JOIN Habit h ON h.id = hl.habit_id
                                JOIN Category c ON c.id = h.category_id
                                WHERE hl.date = ?""", (today_date,), fetch= "all")
        if result:
            return [dict(row) for row in result]
        else:
            return None
    def fetch_habit_logs_per_habit(self, habit_id):
        result= self.execute("""SELECT h.name AS habit_name, c.name AS category_name, hl.done, hl.complete_at,hl.date FROM HabitLog hl
                                JOIN Habit h ON h.id = hl.habit_id
                                JOIN Category c ON c.id = h.category_id
                                WHERE hl.habit_id = ?""", (habit_id,), fetch= "all")
class StatDAO(BaseDAO):
    """
    Statistics class for analyzing habits data stored in an SQLite database.

    This class provides several static methods to compute and visualize various
    statistics related to user habits, including:

    - Calculating streaks (consecutive days with completed habits).
    - Tracking daily progress (habits completed today).
    - Analyzing the most frequently completed habits.
    - Visualizing the most productive days.
    - Displaying habits scheduled by day and category.

    All methods connect to the SQLite database "habit_tracker.db" and utilize pandas
    for data manipulation and plotly for generating visualizations.

    Main methods include:
        - streak(daystreak): Calculate the current streak of consecutive active days.
        - progress_bar(): Count habits completed today.
        - most_done(): Frequency of habit completion.
        - longest_streak(): Maximum streak length per habit.
        - longest_daystreak(): Longest overall streak of active days.
        - habits_by_day(): Retrieve habits along with categories and scheduled days.
        - day_with_the_most_habit(): Distribution of habits by day of the week (chart).
        - category_with_the_most_habit(): Distribution of habits by category (chart).
        - Other analytical and visualization functions.

    Designed for use in a habit tracking project to help users understand their
    behavior patterns and track their progress over time.

    Example usage:
        >>> current_streak = Stat.streak(0)
        >>> print(f"Current streak: {current_streak}")

    Note:
        Each method handles its own SQLite connection and closes it after execution.
    """
    def get_habit_streak(self,):
        """
        Calculates the user's current streak of consecutive days with at least one habit marked as done.

        The function fetches all unique dates from the HabitLog table, starting from the most recent,
        and counts how many consecutive days (from yesterday or today backward) the user has completed at least one habit.

        Args:
            daystreak (int): The initial streak value, usually 0.

        Returns:
            int: The total streak of consecutive days with completed habits.

        Notes:
            - The streak only counts days if there is at least one record in HabitLog for that date.
            - The function checks from yesterday or today backward, depending on available dates.

        Example:
            >>> streak_count = Habit.streak(0)
            >>> print(f"Current streak: {streak_count}")
        """
            #Selecting each logs of habit Done
        rows = self.execute("SELECT date FROM HabitLog WHERE complete_at IS NOT NULL ORDER BY date DESC", fetch= "all")
        if not rows:
            return []
        
        return rows
    def get_today_completed_habit(self):
        """
        Calculates the number of habit done today and return the result.

        The function fetches all habits (Name, Done) done.

        Returns:
            int: The number of habit done today.

        Notes:
            - This is mean to be used with the number of today's habits to get a progress bar.

        Example:
            >>> habit_done = Habit.progress_bar()
            >>> print(f"{habit_done}/{number_of_today_habit}")
        """
        today_date = datetime.today().date()
        result = self.execute("SELECT COUNT(*) FROM HabitLog WHERE done = 1 AND date = ?", (today_date,), fetch = "one")


        return result[0] if result else 0
    
    def get_today_number_of_habit(self):
        result = self.execute("SELECT date, COUNT(*) as total_scheduled, SUM(Done) as total_done", fetch = "one")