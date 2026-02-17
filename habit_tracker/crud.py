#Habit tracker with hbait class,
#importing library that I need
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
from datetime import timedelta
import numpy as np
from database import db_conn

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
            cursor.execute("SELECT CategoryID, Name, Description FROM Category")
            categories = cursor.fetchall()
        
        #create a dataframe
        df = pd.DataFrame(categories, columns=['CategoryID', 'Name', 'Description'])
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
            cursor.execute("""INSERT INTO Category (Name, Description) VALUES (?,?)""", (category_name, category_desc))
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
            cursor.execute("""UPDATE Category SET Name = ? ,Description = ? WHERE Name = ?""", (new_category_name, new_category_desc, category_name))
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
            cursor.execute("DELETE FROM Category WHERE CategoryID = ?", (category_id,))
    
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
            cursor.execute("SELECT COUNT(*) FROM Habit WHERE CategoryID = ?", (category_id,))
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
    
    Habits are stored in the 'Habit' table, associated days in 'HabitDays',
    and activity logs in 'HabitLog'. Categories are stored in 'Category' table.
    The 'Settings' table holds metadata like the last reset date.

    Usage example:
        >>> Habit.add_habit()
        >>> todays = Habit.show_today_habit()
        >>> Habit.mark_done()
        >>> Habit.reset_done()
    """
    @staticmethod
    def show_today_habit():
        """
        Returns a list of today's habits based on the current weekday.

        The function fetches all habits that are scheduled for today by joining
        the 'Habit' and 'HabitDays' tables using the current weekday (e.g., "Monday").

        Returns:
                list of tuples: Each tuple contains (Name, HabitID, Done) for today's habits.

        Example:
            >>> habits = show_today_habit()
            >>> for h in habits:
            ...     print(h)
        """
        today = datetime.today().strftime('%A')
        with db_conn() as conn:
            cursor = conn.cursor()
            #selecting the habit of where the Days is today.
            cursor.execute("""SELECT h.Name, h.HabitID, h.Done
                FROM Habit h
                JOIN HabitDays d ON h.HabitID = d.HabitID
                WHERE d.Days = ? """, (today,))
            habits = cursor.fetchall()
        return habits
    
    @staticmethod
    def show_habit():
        """
        Shows all habits with their details.

        This function joins the Habit, HabitDays, and Category tables to return
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
                SELECT h.HabitID, h.Name,h.Description, c.Name 
                ,GROUP_CONCAT(DISTINCT d.Days) AS Days, h.CreateAt
                FROM Habit h
                LEFT JOIN HabitDays d ON h.HabitID = d.HabitID
                LEFT JOIN  Category c ON h.CategoryID= c.CategoryID
                GROUP BY h.HabitID, h.Name, c.Name;
            """)
            habit = cursor.fetchall()
        df = pd.DataFrame(habit, columns= ['HabitID','Habit','Description', 'Category','Days', 'CreateAt'])
        return df
    @staticmethod
    def add_habit(habit_name,habit_desc, category_id,days):
        """
        Adds a new habit and assigns it to specific days.

        Inserts a new habit into the 'Habit' table and associates it with selected
        days in the 'HabitDays' table.

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
            cursor.execute("INSERT INTO Habit (Name, Description, CategoryID) VALUES (?, ?, ?)", (habit_name, habit_desc, category_id))
            #selecting the new habit HabitID
            cursor.execute("SELECT HabitID FROM Habit WHERE Name = ?", (habit_name,))
            habit_id = cursor.fetchone()[0]
            #inserting the habitID with the days choice by the user in the HabitDays table one day by one
            for day in days:
                cursor.execute("INSERT INTO HabitDays (HabitID, Days) VALUES (?, ?)", (habit_id, day))


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
            cursor.execute("SELECT Name, CreateAt FROM Habit WHERE HabitID = ?", (habit_id,))
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
        days in 'HabitDays' with the new list provided.

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
                cursor.execute("UPDATE Habit SET Name = ? WHERE HabitID = ?", (habit_new_name, habit_id,))
            if category_id is not None:
                cursor.execute("UPDATE Habit SET CategoryID = ? WHERE HabitID = ?", (category_id, habit_id,))
            if len(days) >= 1:
                cursor.execute("DELETE FROM HabitDays WHERE HabitID = ?", (habit_id,))
                for day in days:
                    cursor.execute("INSERT INTO HabitDays VALUES(?,?)", ( habit_id, day,))

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
        with db_conn() as conn:
            cursor = conn.cursor()
            #save the habitID with the datedone in HabitLog
            cursor.execute(
                "INSERT OR REPLACE INTO HabitLog(HabitID, DateDone) VALUES (?, DATE('now'))",
                (habit_id, ))
            #update the status done in the table Habit
            cursor.execute(
                "UPDATE Habit SET Done = 1 WHERE HabitID = ?",
                (habit_id,))
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
        with db_conn() as conn:
            cursor = conn.cursor()
            date = datetime.today().strftime("%Y-%m-%d")

            cursor.execute(
                "DELETE FROM HabitLog WHERE HabitID = ? AND DateDone= ?",
                (habit_id, date))
            cursor.execute(
                "UPDATE Habit SET Done = 0 WHERE HabitID = ?",
                (habit_id,))
    @staticmethod
    def reset_done():
        """
        Resets the 'Done' status of all habits if not already reset today.

        Uses a setting stored in the 'Settings' table to ensure habits are
        only reset once per day. If the date has changed, all habits are marked
        as not done and the reset date is updated.

        Example:
            >>> reset_done()
        """
        today = datetime.today().date()
        with db_conn() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT value FROM Settings WHERE key = 'last_reset'")
            last_reset = cursor.fetchone()
            if last_reset is None:
                cursor.execute("UPDATE Habit SET Done = 0")
                cursor.execute("REPLACE INTO Settings(key,value) VALUES ('last_reset', ?)", (str(today),))
                conn.commit()
            elif last_reset[0] != str(today): #if the lastres"t day isn't the same as today so every done status is updated to 0 and the settings to resetdone is replaced into a new date
                cursor.execute("UPDATE Habit SET Done = 0")
                cursor.execute("REPLACE INTO Settings(key,value) VALUES ('last_reset', ?)", (str(today),))
                conn.commit()


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
        conn = sqlite3.connect("habit_tracker.db")
        cursor = conn.cursor()
        #Selecting each logs of habit Done
        cursor.execute("SELECT DISTINCT DateDone FROM HabitLog ORDER BY DateDone DESC")
        done_dates = [datetime.strptime(row[0], "%Y-%m-%d").date() for row in cursor.fetchall()]
        conn.close()

        if not done_dates:
            return 0
        today =datetime.today().date()
        today -= timedelta(days=1)
        #tommorow = today -= timedelta(days=1)

        for date in done_dates: #looping the date from today and went back one day to one day to count the streak
            if date == today:
                daystreak += 1
                today -= timedelta(days=1)
            else :
                today =datetime.today().date()
                if date == today:
                    daystreak += 1
                    today -= timedelta(days=1)

                
        return daystreak
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
        conn = sqlite3.connect("habit_tracker.db")
        cursor = conn.cursor()
        cursor.execute("SELECT Name, Done FROM Habit WHERE Done = 1;  ")
        result = cursor.fetchall()

        conn.close()
        return result
        
    @staticmethod
    def stat():
        conn = sqlite3.connect("habit_tracker.db")
        cursor = conn.cursor()
        cursor.execute("SELECT  Name, DateDone FROM HabitLog")
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["Name", "DateDone)"])
    @staticmethod
    def df_stat_conn():
        conn = sqlite3.connect("habit_tracker.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT h.Name, d.DateDone
            FROM Habit h
            JOIN HabitLog d ON h.HabitID = d.HabitID
            ORDER BY d.DateDone
        """)
        progress = cursor.fetchall()
        conn.close()
        df = pd.DataFrame(progress, columns=['Name', 'DateDone'])
        df['DateDone'] = pd.to_datetime(df['DateDone']).dt.date

        return df
    @staticmethod
    def most_done():
        """
        Calculates how many times each habit has been marked as done.

        Returns:
            pd.DataFrame: A DataFrame with two columns:
                - 'Name': the name of the habit
                - 'Count': how many times the habit was completed

        Notes:
            - This is useful to analyze consistency and long-term performance.
            - Use this with visualizations or ranking systems.

        Example:
            >>> df = Habit.most_done()
            >>> print(df.sort_values("Count", ascending=False))
        """
        conn = sqlite3.connect("habit_tracker.db")
        cursor = conn.cursor()
        #Select Habit Name, Date Done and order by name
        cursor.execute("""
            SELECT h.Name, d.DateDone
            FROM Habit h
            JOIN HabitLog d ON h.HabitID = d.HabitID
            ORDER BY h.Name
        """)
        result = cursor.fetchall()
        conn.close()
        df = pd.DataFrame(result, columns=['Name', 'DateDone'])
        return df
    
    @staticmethod
    def longest_streak():
        """
        Calculates the longest consecutive day streak for each habit.

        Returns:
            plotly.graph_objects.Figure: A bar chart figure showing the longest streak per habit.

        Notes:
            - The streak is based on the dates when the habit was marked as done.
            - Useful to visualize habit consistency over time.
            - Requires the database table Habit and HabitLog with dates of completion.

        Example:
            >>> fig = longest_streak()
            >>> fig.show()
        """
        conn = sqlite3.connect("habit_tracker.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT h.Name, d.DateDone
            FROM Habit h
            JOIN HabitLog d ON h.HabitID = d.HabitID
            ORDER BY h.Name
        """)
        progress = cursor.fetchall()
        conn.close()
        df = pd.DataFrame(progress, columns=['Name', 'DateDone'])
        df['DateDone'] = pd.to_datetime(df['DateDone'])

        streaks = {}
        for habit, group in df.groupby('Name'):
            dates = sorted(group['DateDone'].dt.date.unique())
            longest, current = 1, 1
            
            for i in range(1, len(dates)):
                if dates[i] == dates[i-1] + timedelta(days=1):
                    current += 1
                else:
                    longest = max(longest, current)
                    current = 1
            longest = max(longest, current)
            
            streaks[habit] = longest

        streak_df = pd.DataFrame(list(streaks.items()), columns=['Habit', 'Longest Streak'])

        # Create bar chart
        fig = px.bar(
            streak_df,
            x='Habit',
            y='Longest Streak',
            color='Habit',
            title='Longest Streak per Habit'
        )
        return fig
    
    @staticmethod
    def longest_daystreak():
        """
        Calculates the longest streak of consecutive days on which at least one habit was completed.

        Returns:
            int: The length of the longest streak in days.

        Notes:
            - The streak counts continuous calendar days with any habit done.
            - Returns 0 if no habits have been completed yet.

        Example:
            >>> longest = longest_daystreak()
            >>> print(f"Longest active streak: {longest} days")
        """
        conn = sqlite3.connect("habit_tracker.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT DateDone FROM HabitLog ORDER BY DateDone")
        dates = cursor.fetchall()
        conn.close()

        if not dates:
            return 0
        
        # Convertir en date simple
        dates = [datetime.strptime(d[0], "%Y-%m-%d").date() for d in dates]
        
        longest = 1
        current = 1
        
        for i in range(1, len(dates)):
            if dates[i] == dates[i-1] + timedelta(days=1):
                current += 1
            else:
                longest = max(longest, current)
                current = 1
        
        longest = max(longest, current)
        return longest
    @staticmethod
    def longest_streak_habit(habit_name) :
        """
        Calculates the longest consecutive streak for each habit, considering only the scheduled days for that habit.

        Returns:
            dict: A dictionary where keys are habit IDs and values are the longest streaks as integers.

        Notes:
            - The streak advances only on scheduled days (e.g., Mon, Wed, Fri).
            - Uses Habit, HabitDays, and HabitLog tables.
            - Dates are parsed from strings to Python date objects.

        Example:
            >>> streaks = longest_streak_habit()
            >>> for habit_id, streak in streaks.items():
            ...     print(f"Habit {habit_id} longest streak: {streak}")
        """
        conn = sqlite3.connect("habit_tracker.db")
        cursor = conn.cursor()
        #I take the habit info , name, and days that the habit
        habit =cursor.execute("""SELECT h.HabitID, h.Name,GROUP_CONCAT(DISTINCT d.Days)
                        FROM Habit h
                        WHERE Habit h is ?
                        JOIN HabitDays d ON h.HabitID = d.HabitID
                        GROUP BY h.HabitID, h.Name
                            """).fetchall()
        
        logs = cursor.execute("SELECT HabitID, DateDone FROM HabitLog ORDER BY HabitID, DateDone").fetchall()
        conn.close()

        done_by_habit = defaultdict(list)
        for hid, date_str in logs:
    # Convertir la date (str) en date Python
            done_by_habit[hid].append(datetime.strptime(date_str, "%Y-%m-%d").date())
        
        if not dates:
            return 0
        dates = sorted(dates)
        longest = current = 1

        for i in range(1, len(dates)):
            prev = dates[i - 1]
            expected = prev

            # Avancer jusqu'au prochain jour programmé
            while True:
                expected += timedelta(days=1)
                if expected.weekday() in scheduled_days:
                    break
            
            # Si la date courante est la date attendue, on continue la streak
            if dates[i] == expected:
                current += 1
            else:
                longest = max(longest, current)
                current = 1

        return max(longest, current)
    @staticmethod
    def most_productive_days():
        """
        Retrieves the days with the highest number of habits completed.

        Returns:
            plotly.graph_objects.Figure: A bar chart showing habit counts per day sorted descending.

        Notes:
            - Useful to identify peak productivity days.
            - Data grouped by DateDone in HabitLog.

        Example:
            >>> fig = most_productive_days()
            >>> fig.show()
        """
        conn = sqlite3.connect("habit_tracker.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DateDone, COUNT(*) AS DoneCount
            FROM HabitLog
            GROUP BY DateDone
            ORDER BY DoneCount DESC
        """)
        df = cursor.fetchall()
        df = pd.DataFrame(df, columns=["DateDone", "DoneCount"])
        df = df.sort_values(by = "DoneCount", ascending = False).reset_index()
        fig = px.bar(df, x="DateDone", y="DoneCount",
             title="Habit done by days:",
             labels={"DateDone": "Date", "DoneCount": "Habit Done"})
        return fig
    @staticmethod
    def most_productive_days_top3():
        """
        Retrieves the top 3 days with the lowest number of habits completed.

        Returns:
            plotly.graph_objects.Figure: A bar chart showing the 3 days with fewest habits done.

        Notes:
            - Useful to analyze least productive days.
            - Data grouped by DateDone in HabitLog.

        Example:
            >>> fig = most_productive_days_top3()
            >>> fig.show()
        """
        conn = sqlite3.connect("habit_tracker.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DateDone, COUNT(*) AS DoneCount
            FROM HabitLog
            GROUP BY DateDone
            ORDER BY DoneCount DESC
        """)
        df = cursor.fetchall()
        df = pd.DataFrame(df, columns=["DateDone", "DoneCount"])
        df = df.sort_values(by = "DoneCount", ascending = True).reset_index().head(3)
        fig = px.bar(df, x="DateDone", y="DoneCount",
             title="Habit done by days:",
             labels={"DateDone": "Date", "DoneCount": "Habit Done"})
        return fig
    @staticmethod
    def habits_by_day():
        """
        Retrieves all habits along with their categories and scheduled days.

        Returns:
            pd.DataFrame: DataFrame with columns ['Name', 'Category', 'Days'] representing
            habit name, its category, and the scheduled days.

        Notes:
            - Useful to overview habit scheduling.
            - Joins Habit, HabitDays, and Category tables.

        Example:
            >>> df = habits_by_day()
            >>> print(df.head())
        """
        conn = sqlite3.connect("habit_tracker.db")
        cursor = conn.cursor()
        cursor.execute("SELECT h.Name, c.Name ,d.Days, h.CreateAt FROM Habit h JOIN HabitDays d ON h.HabitID = d.HabitID LEFT JOIN Category c ON h.CategoryID = c.CategoryID ORDER BY h.Name, d.Days", )
        habit_by_day = cursor.fetchall()
        df= pd.DataFrame(habit_by_day, columns=['Name','Category', 'Days', 'CreateAt'])
    
        return df
    #ROULETTE AVEC Jour et nombre d'habit par jour
    @staticmethod
    def day_with_the_most_habit():
        """
        Shows the distribution of the number of habits scheduled per day of the week.

        Returns:
            plotly.graph_objects.Figure: A pie chart representing habit counts by day.

        Notes:
            - Helps identify which days have the most or fewest habits scheduled.

        Example:
            >>> fig = day_with_the_most_habit()
            >>> fig.show()
        """
        conn= sqlite3.connect('habit_tracker.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.Days , COUNT(d.HabitID) AS HabitCount
            FROM HabitDays d
            JOIN Habit h ON h.HabitID = d.HabitID
            GROUP BY d.Days
            ORDER BY d.Days
        """)
        result = cursor.fetchall()
        df= pd.DataFrame(result, columns=["Days", "HabitCount"])
        fig = px.pie(
        df,
        values="HabitCount",
        names="Days",
        title="Number of habit by days",
        hover_name= "Days",
        hover_data= "HabitCount"
                                     )
        fig.update_traces(textposition='inside', textinfo='percent+label')

        return fig
        #roulette avec category hover count of habit in the cat
    @staticmethod
    def category_with_the_most_habit():
        """
        Shows the distribution of the number of habits per category.

        Returns:
            plotly.graph_objects.Figure: A pie chart representing habit counts by category.

        Notes:
            - Useful to see which categories contain most habits.

        Example:
            >>> fig = category_with_the_most_habit()
            >>> fig.show()
        """
        conn= sqlite3.connect('habit_tracker.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.Name, COUNT(h.HabitID) AS HabitCount
            FROM Habit h
            JOIN Category c ON c.CategoryID = h.CategoryID
            GROUP BY c.Name
            ORDER BY HabitCount Desc
        """)
        result = cursor.fetchall()
        conn.close()
        df= pd.DataFrame(result, columns=["Category", "HabitCount"])
        fig = px.pie(
        df,
        values="HabitCount",
        names = "Category",
        title="Number of habit by category",
        hover_name= "Category",
        hover_data= "HabitCount",
                                     )
        fig.update_traces(textposition='inside', textinfo='percent+label')

        return fig
    #roulette en %
    @staticmethod
    def category_the_most_done():
        
        """
        Shows the categories with the highest count of completed habits.

        Returns:
            plotly.graph_objects.Figure: A pie chart representing the percentage of completed habits by category.

        Notes:
            - Helps analyze which habit categories are most actively completed.

        Example:
            >>> fig = category_the_most_done()
            >>> fig.show()
        """
        conn= sqlite3.connect('habit_tracker.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.Name, COUNT(l.DateDone) as DoneCount
            FROM Habit h
            JOIN HabitLog l ON l.HabitID= h.HabitID
            JOIN Category c ON c.CategoryID = h.CategoryID
            GROUP BY c.Name
            ORDER BY DoneCount DESC
        """)
        result = cursor.fetchall()
        conn.close()
        df= pd.DataFrame(result, columns=["Category", "DoneCount"])
        fig = px.pie(
        df,
        values="DoneCount",
        names = "Category",
        title="Category with the most habit done in %",
        hover_name= "Category",
        hover_data= "DoneCount"
                                     )
        fig.update_traces(textposition='inside', textinfo='percent+label')

        return fig
    @staticmethod
    def days_the_most_done():
        """
        Shows the distribution of habits completed by day of the week.

        Returns:
            plotly.graph_objects.Figure: A pie chart representing percentage of habits done by day of week.

        Notes:
            - Uses HabitLog and HabitDays tables.
            - Groups data by day of week (Monday, Tuesday, etc.)

        Example:
            >>> fig = days_the_most_done()
            >>> fig.show()
        """
        conn= sqlite3.connect('habit_tracker.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.DateDone, d.Days, COUNT(l.DateDone) as DoneCount
            FROM Habit h
            LEFT JOIN HabitLog l ON l.HabitID= h.HabitID
            LEFT JOIN HabitDays D ON d.HabitID = h.HabitID
            GROUP BY l.DateDone
            ORDER BY DoneCount DESC
        """)
        result = cursor.fetchall()
        conn.close()
        df= pd.DataFrame(result, columns=["DateDone","Days", "DoneCount"])
        df["DateDone"] = pd.to_datetime(df["DateDone"])
        df["DayOfWeek"] = df["DateDone"].dt.day_name()
        grouped = df.groupby("DayOfWeek").size().reset_index(name="DoneCount")
        fig = px.pie(
                grouped,
                values="DoneCount",
                names="DayOfWeek",
                title="Habits done by day of week (%)",
                hover_data=["DoneCount"]
                )
        fig.update_traces(textposition='inside', textinfo='percent+label')

        return fig
