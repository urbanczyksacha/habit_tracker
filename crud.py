#Habit tracker with hbait class,
#importing library that I need
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
from datetime import timedelta
import numpy as np
from database.database import db_conn

class Days: 
    @staticmethod
    def show_days(): 
        days_of_the_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] 
        for i, day in enumerate(days_of_the_week, start = 1): 
            print(f"{i}. {day}") 
            return days_of_the_week
        
#creating category class to output the predefined category, save new one, deleting category
#The class category is used to have everythings with category action, like deleting, adding, choosing.
class Category :
    """
    Manages categories of habits stored in the SQLite database.

    Provides static methods to:
      - Show all categories.
      - Add, modify, and delete categories.
      - Validate deletion by checking linked habits.

    Categories help organize habits into groups for better management.

    Usage example:
        >>> Category.add_category("Health", "Physical and mental well-being")
        >>> df = Category.show_category()
        >>> Category.modify_category("Fitness", "Updated description", "Health")
        >>> Category.delete_category(3)
    """
    @staticmethod
    def show_category():
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
            >>> df = ClassName.show_category()
            >>> print(df.head())
        """
        #connecting in the data base, selecting and export to a dataframe
        with db_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description FROM Category")
            categories = cursor.fetchall()
        
        #create a dataframe
        df = pd.DataFrame(categories, columns=['ID', 'Name', 'Description'])
        return df
        
    @staticmethod
    def add_category(category_name, category_desc):
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
        with db_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO Category (name, description) VALUES (?,?)""", (category_name, category_desc))
    @staticmethod
    def modify_category(new_category_name, new_category_desc,category_name):
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
            >>> modify_category("Fitness", "Updated description", "Health")
        """
        with db_conn() as conn:
            cursor = conn.cursor()
            #Uptading the sql row to not recreate a new id and to keep the same category and just modify it
            cursor.execute("""UPDATE Category SET name = ? ,description = ? WHERE name = ?""", (new_category_name, new_category_desc, category_name))
    @staticmethod
    def delete_category(category_id):
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
        with db_conn() as conn:
            cursor = conn.cursor()
            #deleting the entire row where the category ID is
            cursor.execute("DELETE FROM Category WHERE id = ?", (category_id,))
    
    @staticmethod
    def delete_category_validation(category_id):
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
        with db_conn() as conn:
            cursor = conn.cursor()
            #Count the number of habit linked with the category that the user want to delete
            cursor.execute("SELECT COUNT(*) FROM Habit WHERE category_id = ?", (category_id,))
            count = cursor.fetchone()[0]
        return count
            


class Habit:
    """
    Manages habits for tracking daily tasks with persistence in a SQLite database.

    This class provides static methods to:
      - Show today's habits or all habits with details.
      - Add, delete, and modify habits.
      - Mark habits as done or undone.
      - Reset daily 'done' status of all habits.
    
    Habits are stored in the 'Habit' table, associated days in 'HabitSchedule',
    and activity logs in 'HabitLog'. Categories are stored in 'Category' table.
    The 'Settings' table holds metadata like the last reset date.

    Usage example:
        >>> Habit.add_habit()
        >>> todays = Habit.show_today_habit()
        >>> Habit.mark_done()
        >>> Habit.reset_done()
    """
    @staticmethod
    def daily_habit_log():
        today = datetime.today().strftime('%A')
        today_date = datetime.today().date()
        with db_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM HabitLog WHERE date = (?)", (today_date,))
            result = cursor.fetchall()
            if not result:
                #selecting the habit of where the Days is today.
                cursor.execute("""SELECT h.name, h.id
                    FROM Habit h
                    JOIN HabitSchedule d ON h.id = d.habit_id
                    WHERE d.day_of_the_week = ? """, (today,))
                habits = cursor.fetchall()
                for name, id in habits:
                    cursor.execute("INSERT INTO HabitLog (habit_id, date) VALUES (?,?)", (id,today_date))
                    conn.commit()
    
    @staticmethod
    def show_today_habit():
        """
        Returns a list of today's habits based on the current weekday.

        The function fetches all habits that are scheduled for today by joining
        the 'Habit' and 'HabitSchedule' tables using the current weekday (e.g., "Monday").

        Returns:
                list of tuples: Each tuple contains (Name, HabitID, Done) for today's habits.

        Example:
            >>> habits = show_today_habit()
            >>> for h in habits:
            ...     print(h)
        """
        today_date = datetime.today().date()
        with db_conn() as conn:
            cursor = conn.cursor()
            #selecting the habit of where the Days is today.
            cursor.execute("""SELECT h.id, h.name, hl.done
                FROM HabitLog hl
                JOIN Habit h ON h.id = hl.habit_id
                WHERE hl.date = ? """, (today_date,))
            habits = cursor.fetchall()

        return habits
    def show_habit_by_day():
        with db_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT h.name, h.description, c.name, hs.day_of_the_week
                           FROM Habit h
                           JOIN Category c ON h.category_id = c.id 
                           JOIN HabitSchedule hs ON h.id = hs.habit_id""")
            result = cursor.fetchall()
            return result
    @staticmethod
    def show_habit():
        """
        Shows all habits with their details.

        This function joins the Habit, HabitSchedule, and Category tables to return
        detailed information about each habit including its ID, name, associated
        category, days of the week, and creation date.

        Returns:
            pd.DataFrame: Columns are ['HabitID','Habit', 'Category','Days', 'CreateAt'].

        Example:
            >>> df = show_habit()
            >>> print(df)
        """
        with db_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT h.id, h.name,h.description, c.name 
                ,GROUP_CONCAT(DISTINCT d.day_of_the_week) AS days, h.create_at
                FROM Habit h
                LEFT JOIN HabitSchedule d ON h.id = d.habit_id
                LEFT JOIN  Category c ON h.category_id= c.id
                GROUP BY h.id, h.name, c.name;
            """)
            habit = cursor.fetchall()
        df = pd.DataFrame(habit, columns= ['HabitID','Habit','Description', 'Category','Days', 'CreateAt'])
        return df
    @staticmethod
    def add_habit(habit_name,habit_desc, category_id,days):
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
        with db_conn() as conn:
            cursor = conn.cursor()
            #Inserting user input habit_name and category-id in the database, the other CreateAt and the HabitID is automated in the sql table
            cursor.execute("INSERT INTO Habit (name, description, category_id) VALUES (?, ?, ?)", (habit_name, habit_desc, category_id))
            habit_id = cursor.lastrowid
            cursor.execute("SELECT create_at FROM Habit WHERE id = (?)", (habit_id,))
            habit_create_at = cursor.fetchone()
            cursor.execute("INSERT INTO HabitHistory (habit_id, name, description, category_id, create_at) VALUES (?, ?, ?,?,?)", (habit_id, habit_name, habit_desc, category_id, habit_create_at,))
            #inserting the habitID with the days choice by the user in the HabitSchedule table one day by one
            for day in days:
                cursor.execute("INSERT INTO HabitSchedule (habit_id, day_of_the_week) VALUES (?, ?)", (habit_id, day))
                conn.commit()


    @staticmethod
    def delete_habit(habit_id):
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
        with db_conn() as conn:
            cursor = conn.cursor()
            #selecting the habit who's gonna be deleted
            cursor.execute("SELECT name, create_at FROM Habit WHERE HabitID = ?", (habit_id,))
            deleted_habit = cursor.fetchone()
            name = deleted_habit[0]
            date = deleted_habit[1]
                #inserting the full row of the deleting habit into the HabitHistory table
            cursor.execute("INSERT INTO HabitHistory (HabitID, Name, Date) VALUES (?,?,?)", (habit_id,name, date,))
            cursor.execute("DELETE FROM Habit WHERE HabitID = ?", (habit_id,))

    @staticmethod
    def modify_habit(habit_new_name,category_id, habit_id, days):
        """
        Modifies a habit's name, category, and scheduled days.

        This function updates the habit in the database and resets its assigned
        days in 'HabitSchedule' with the new list provided.

        Args:
            habit_new_name (str): New name for the habit.
            category_id (int): Updated category ID.
            habit_id (int): The ID of the habit to modify.
            days (list of str): New days for the habit.

        Raises:
            sqlite3.Error: If update operations fail.

        Example:
            >>> modify_habit("Workout", 2, 1, ["Tuesday", "Thursday"])
        """
        with db_conn() as conn:
            cursor = conn.cursor()
            habit_new_name = habit_new_name.strip()
            if len(habit_new_name) >= 1 :
                cursor.execute("UPDATE Habit SET Name = ? WHERE id = ?", (habit_new_name, habit_id,))
            if category_id is not None:
                cursor.execute("UPDATE Habit SET category_id = ? WHERE id = ?", (category_id, habit_id,))
            if len(days) >= 1:
                cursor.execute("DELETE FROM HabitSchedule WHERE habit_id = ?", (habit_id,))
                for day in days:
                    cursor.execute("INSERT INTO HabitSchedule VALUES(?,?)", ( habit_id, day,))

    @staticmethod
    def mark_done(habit_id):
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
        with db_conn() as conn:
            cursor = conn.cursor()
            #update the status done in the table Habit
            cursor.execute(
                "UPDATE Habitlog SET Done = 1 ,complete_at = ? WHERE habit_id = ? AND date = ?",
                (today,habit_id, today_date,))
    @staticmethod
    def unmark_done(habit_id):
        """
        Cancels the 'done' status of a habit for today.

        Deletes the habit from the 'HabitLog' table for today's date and
        resets the 'Done' field to 0.

        Args:
            habit_id (int): The ID of the habit to unmark.

        Example:
            >>> unmark_done(2)
        """
        today_date = datetime.today().date()
        with db_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE HabitLog SET Done = 0, complete_at = NULL WHERE habit_id = ? AND date = ?",
                (habit_id, today_date,))


class Stat:
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
    @staticmethod
    def streak(daystreak):
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
        with db_conn() as conn:
            cursor = conn.cursor()
            #Selecting each logs of habit Done
            cursor.execute("SELECT date FROM HabitLog WHERE complete_at IS NOT NULL ORDER BY date DESC")
            rows = cursor.fetchall()

        if not rows:
            return 0
        else:
            today =datetime.today().date()
            last_completed = datetime.strptime(rows[0][0], "%Y-%m-%d").date()
            
            if (today - last_completed).days > 1:
                return 0
            else:
                streak = 0
                expected_date = last_completed

                for row in rows:
                    row_date = datetime.strptime(row[0], "%Y-%m-%d").date()

                    if row_date == expected_date:
                        streak +=1
                        expected_date -= timedelta(days=1)
                    else:
                        break

                    
            return streak
    @staticmethod
    def progress_bar():
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
        with db_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM HabitLog WHERE done = 1 AND date = ?", (today_date,))
            result = cursor.fetchone()[0]


        return result
    
    def get_daily_completion():
        with db_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT date, COUNT(*) as total_scheduled, SUM(Done) as total_done")

Habit.daily_habit_log()