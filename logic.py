#This file will be use to compute, none database manipulation is allowed
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from crud import HabitDAO
def init_app():
    HabitDAO.add_daily_habit_log()
class HabitNotFound(Exception):
    pass
class CategoryNotFound(Exception):
    pass
class HabitService:
    def __init__(self,habit_dao) -> None:
        self.habit_dao = habit_dao
    def get_today_habit_df(self):
        rows = self.habit_dao.fetch_habit()
        df = pd.DataFrame(rows)
        if df.empty:
            raise HabitNotFound("No habit for today.")
        return df
    def get_today_habit(self):
        rows = self.habit_dao.fetch_habit()
        if not rows:
            raise HabitNotFound("No habit for today.")

        return rows
    def get_habit_by_day_df(self, selected_day):
        rows = self.habit_dao.fetch_habit_by_day()
        df = pd.DataFrame(rows)
        df_filtre = df[df["Day"] == selected_day]
        if len(df_filtre) == 0:
            raise HabitNotFound("No habit for today.")
        else:
            df_filtre = df_filtre.drop(columns= ["Day"])
            return df_filtre
    def add_habit(self,habit_name, habit_desc, category_id, days):
        self.habit_dao.add_habit(habit_name, habit_desc, category_id, days)
    def delete_habit(self,habit_id):
        self.habit_dao.delete_habit(habit_id)
    def update_habit(self,habit_new_name,category_id, habit_id, days):
        self.habit_dao.update_habit(habit_new_name,category_id, habit_id, days)
    def update_done(self,habit_id,done):
        self.habit_dao.update_done(habit_id,done)

class CategoryService:
    def __init__(self, category_dao) -> None:
        self.category_dao = category_dao
    def get_category(self):
        result = self.category_dao.fetch_category()
        if not result:
            raise CategoryNotFound("No category found")
        return result
    def get_category_df(self):
        rows = self.category_dao.fetch_category()
        df = pd.DataFrame(rows)
    def add_category(self,category_name, category_desc):
        self.category_dao.add_category(category_name, category_desc)
    def update_category(self,new_category_name, new_category_desc,category_name):
        self.category_dao.update_category(new_category_name, new_category_desc,category_name)
    def delete_category(self,category_id):
        self.category_dao.delete_category(category_id)

class StatService:
    def __init__(self, habit_dao, category_dao, stat_dao, habit_log_dao) -> None:
        self.habit_dao = habit_dao
        self.category_dao= category_dao
        self.stat_dao =  stat_dao
        self.habit_log_dao = habit_log_dao
        
    #into the stat tabs the user will have access to smart statistical plot, the goal is to give overall information with text that could help to improve productivity
    def get_habit_streak(self):
        rows = self.habit_log_dao.get_habit_streak()
        today =datetime.today().date()
        last_completed = datetime.strptime(rows[0][0], "%Y-%m-%d").date()
        if not rows:
            return 0
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
    def get_today_number_of_habit(self):
        result = self.stat_dao.get_today_number_of_habit()
        return result
    def progress_bar(self):
        streak = self.get_habit_streak()
        number_of_habit = self.get_today_number_of_habit()
        progress = streak/number_of_habit
        return progress
    def completation_rate_global(self):
        pass
    def category_ranking(self):
        pass
    def most_productive_hour(self,):
        rows = self.habit_log_dao.fetch_habit_log()
        df = pd.DataFrame(rows, columns= ["habit_id", "done", "complete_at", "date"])
        df["hour"] = pd.to_datetime(df["complete_at"]).dt.hour
        return df.groupby("hour").size().idxmax() #its not exactly what I want, I wwant a things like a fourchette or something like this where i can see the % of habit make into this fork
    def most_completed_days(self):
        "show days by week with % of habit completed"
        pass
    def most_productive_day(self):
        pass
    def daystreak_predictor(self):
        pass
    def longuest_streak(self):
        pass
class Utils:
    @staticmethod
    def words():
        #list of sentence
        tracker_phrases = [
                            # Positive (30%)
                            "Every small step counts.",
                            "Today is a new opportunity to grow.",
                            "You are stronger than you think.",
                            "Keep going, your efforts are paying off.",
                            "Smile and embrace the journey.",
                            "Believe in yourself and your abilities.",
                            "You are capable of amazing things.",
                            "Progress, not perfection, is the goal.",
                            "Celebrate every little achievement.",

                            # Famous Quotes (15%)
                            "Imagination is more important than knowledge. – Albert Einstein",
                            "Science is a way of thinking much more than it is a body of knowledge. – Carl Sagan",
                            "Nature is relentless and unchangeable, and it is indifferent as to whether its hidden reasons and actions are understandable to man. – Galilée",
                            "Man is condemned to be free. – Sartre",
                            "A theory is something nobody believes, except the person who made it. An experiment is something everybody believes, except the person who made it. – Max Planck",

                            # Goals (30%)
                            "Focus on what matters most today.",
                            "Break big goals into small, achievable steps.",
                            "Each day brings you closer to your dreams.",
                            "Success is built one habit at a time.",
                            "Keep your eye on the target, not the obstacle.",
                            "Progress is the sum of consistent actions.",
                            "Set clear intentions for every task.",
                            "Your future self will thank you for what you do today.",
                            "Goals are dreams with deadlines.",

                            # Discipline (15%)
                            "Discipline is the bridge between goals and achievement.",
                            "Small daily efforts create lasting results.",
                            "Consistency beats motivation every time.",
                            "Stick to your plan even when it’s tough.",
                            "True freedom comes from self-discipline.",

                            # Empathy (15%)
                            "Treat yourself with the kindness you offer others.",
                            "Understanding others begins with listening.",
                            "Compassion is a strength, not a weakness.",
                            "Offer encouragement, even on hard days.",
                            "Your empathy can change someone’s world today."
                        ]

        days_since = 10
        category_since = "Sport"
        alert = [f"It's been {days_since} days that you haven't completed a habit from {category_since} category", "It's your birthday", "Hello sunshine","You are near your goal don't give up"]
        random = np.random.randint(low=0, high= 30)
        sentence = tracker_phrases[random]
        return sentence
    @staticmethod
    def get_days(): 
        days_of_the_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] 
        for i, day in enumerate(days_of_the_week, start = 1): 
            print(f"{i}. {day}") 
            return days_of_the_week

