import pandas as pd
from datetime import datetime, timedelta


#For the daily
def current_daystreak(habit_logs, today_date):
    """
    Calculate the current consecutive day streak from habit logs.
    The "daystreak" count if at least one habit is done by day.

    Args:
        habit_logs (list[dict]): List of habit log dictionaries, each containing
            a 'date' key in 'YYYY-MM-DD' format.
        today_date (datetime.date): Today's date to check streak validity.

    Returns:
        int: Current day streak. Returns 0 if no streak or logs are empty.

    Example:
        >>> logs = [{"date": "2026-03-13"}, {"date": "2026-03-12"}]
        >>> current_daystreak(logs, date(2026, 3, 13))
        2
    """
    if not habit_logs:
        return 0
    dates = sorted(set(map(lambda log: datetime.strptime(log["date"], "%Y-%m-%d").date(), habit_logs)), reverse= True)
    last_completed = dates[0]

    if (today_date - last_completed).days > 1:
        return 0
    else:
        streak = 0
        expected_date = last_completed

        for date in dates:
            if date  == expected_date:
                streak +=1
                expected_date -= timedelta(days=1)
            else:
                break
    return streak
def longuest_daystreak(habit_logs):
    """
    Calculate the longest consecutive day streak from habit logs.
    The streak count if at least one habit is done.

    Args:
        habit_logs (list[dict]): List of habit log dictionaries, each containing
            a 'date' key in 'YYYY-MM-DD' format.

    Returns:
        int: Longest consecutive day streak found in the logs.

    Example:
        >>> logs = [{"date": "2026-03-11"}, {"date": "2026-03-12"}, {"date": "2026-03-14"}]
        >>> longuest_daystreak(logs)
        2
    """
    if not habit_logs:
        return 0
    else:
        dates = sorted(set(map(lambda log: datetime.strptime(log["date"], "%Y-%m-%d").date(), habit_logs)))

        max_streak= 1 
        current_streak= 1

        for i in range(1, len(dates)):
            if dates[i] == dates[i-1] + timedelta(1):
                current_streak +=1
                max_streak = max(max_streak,current_streak)
            else:
                current_streak = 1
    return max_streak
def completion_rate(habit_logs):
    """
    Calculate the overall completion rate from a list of habit logs.

    Args:
        habit_logs (list[dict]): List of habit log dictionaries, each containing
            a 'done' key with an integer value (1 = done, 0 = not done).

    Returns:
        tuple: A tuple containing:
            - done (int): Number of completed habits.
            - not_done (int): Number of uncompleted habits.
            - rate (float): Completion rate as a percentage (0-100).

    Example:
        >>> logs = [{"done": 1}, {"done": 0}, {"done": 1}]
        >>> completion_rate(logs)
        (2, 1, 66.67)
    """
    total= len(habit_logs)
    if total ==0:
        return 0,0,0
    done = len(list(filter(lambda log: log["done"], habit_logs )))
    not_done = total - done
    rate = (done/total)*100
    return done, not_done, rate
def daily_completion_rate(habit_logs, today):
    """
    Calculate the completion rate for a specific day.

    Args:
        habit_logs (list[dict]): List of habit log dictionaries, each containing
            a 'date' key in 'YYYY-MM-DD' format and a 'done' key.
        today (datetime.date): The date to filter logs by.

    Returns:
        tuple: A tuple containing done (int), not_done (int), rate (float).

    Example:
        >>> logs = [{"date": "2026-03-13", "done": 1}, {"date": "2026-03-12", "done": 0}]
        >>> daily_completion_rate(logs, date(2026, 3, 13))
        (1, 0, 100.0)
    """
    filtered = list(filter(lambda log: datetime.strptime(log["date"], "%Y-%m-%d").date() == today, habit_logs))
    return completion_rate(filtered)

def productivity_comparaison(habit_logs_per_date, today_date):
    """
    Compare today's completion rate with yesterday's.

    Args:
        habit_logs_per_date (list[dict]): List of habit log dictionaries containing
            'date' and 'done' keys.
        today_date (datetime.date): Today's date.

    Returns:
        int: Difference in completion rate between today and yesterday.
            Positive means more productive, negative means less productive.

    Example:
        >>> productivity_comparaison(logs, date(2026, 3, 13))
        15
    """
    yesterday_date = today_date - timedelta(1)

    today_logs = list(filter(lambda log: datetime.strptime(log["date"], "%Y-%m-%d").date() == today_date, habit_logs_per_date))
    yesterday_logs = list(filter(lambda log: datetime.strptime(log["date"], "%Y-%m-%d").date() == yesterday_date, habit_logs_per_date))

    _, _, today_completion_rate = completion_rate(today_logs)
    _, _, yesterday_completion_rate = completion_rate(yesterday_logs)
    productivity_rate = today_completion_rate - yesterday_completion_rate
    return int(productivity_rate)

def best_productivity_period(today_habit_logs):
    """
    Identify the most productive hours of the day based on completed habits.

    Args:
        today_habit_logs (list[dict]): List of habit log dictionaries containing
            'complete_at' key in 'YYYY-MM-DD HH:MM:SS' format.

    Returns:
        tuple: A tuple containing:
            - activity_per_hours (pd.Series): Number of completions per hour range.
            - df (pd.DataFrame): Filtered logs with added 'hour' and 'hour_range' columns.
        Returns (None, None) if no logs or no completed habits.

    Example:
        >>> activity, df = best_productivity_period(today_logs)
    """

    if not today_habit_logs:
        return None, None
    
    filtered = list(filter(lambda log: log["complete_at"] is not None, today_habit_logs))
    if not filtered:
        return None, None
    filtered = (list(map(lambda log: {**log, "complete_at": datetime.strptime(log["complete_at"], "%Y-%m-%d %H:%M:%S"),
                                      'hour': datetime.strptime(log["complete_at"],"%Y-%m-%d %H:%M:%S").hour},filtered)))
    
    df = pd.DataFrame(filtered)
    bins = list(range(0,25))
    labels = [f"{h}-{h+1}" for h in range(24)]
    df["hour_range"] = pd.cut(df["hour"], bins, right= False, labels= labels)
        
    activity_per_hours = df.groupby("hour_range", observed= False).size()

    return activity_per_hours, df

#For weekly

def weekly_completion_rate(habit_logs, week_start, week_end):
    """
    Calculate the completion rate for a specific week.

    Args:
        habit_logs (list[dict]): List of habit log dictionaries containing
            'date' and 'done' keys.
        week_start (datetime.date): Start date of the week (inclusive).
        week_end (datetime.date): End date of the week (inclusive).

    Returns:
        tuple: A tuple containing done (int), not_done (int), rate (float).

    Example:
        >>> weekly_completion_rate(logs, date(2026, 3, 9), date(2026, 3, 15))
        (10, 4, 71.43)
    """
    filtered = list(filter(lambda log: week_start <= datetime.strptime(log["date"], "%Y-%m-%d").date() <= week_end, habit_logs))
    return completion_rate(filtered)

def weekly_completion_day_per_day(habit_logs, week_start, week_end):
    """
    Calculate the completion rate for each day of a given week.

    Args:
        habit_logs (list[dict]): List of habit log dictionaries containing
            'date' and 'done' keys.
        week_start (datetime.date): Start date of the week (inclusive).
        week_end (datetime.date): End date of the week (inclusive).

    Returns:
        pd.DataFrame: DataFrame with columns 'date', 'date_label', 'completed',
            'total', and 'completion_rate' for each day in the week.

    Example:
        >>> df = weekly_completion_day_per_day(logs, date(2026, 3, 9), date(2026, 3, 15))
    """
    filtered = list(filter(lambda log: week_start <=  datetime.strptime(log["date"], "%Y-%m-%d").date() <= week_end, habit_logs))
    filtered = list(map(lambda log : {**log, 'date_label': datetime.strptime(log["date"], "%Y-%m-%d").date().strftime("%A - %d-%m")}, filtered))
    df = pd.DataFrame(filtered)
    result = df.groupby(["date", "date_label"])["done"].agg(completed = "sum", total ="count").reset_index()
    result["completion_rate"] = result["completed"]/result["total"]
    return result
def weekly_best_productivity_day():
    pass
def weekly_best_productivity_period():
    pass

#For habit
def longuest_habit_streak(habit_logs):
    """
    Calculate the longest streak for each habit.

    Args:
        habit_logs (list[dict]): List of habit log dictionaries containing
            'habit_name', 'done', and 'date' keys.

    Returns:
        dict: Dictionary mapping habit names to their longest streak.
            Example: {"Morning Run": 7, "Meditation": 3}

    Example:
        >>> longuest_habit_streak(logs)
        {"Morning Run": 7, "Meditation": 3}
    """
    done_logs = list(filter(lambda log: log["done"] == 1, habit_logs))
    habits_names = list(set(map(lambda log: log["habit_name"], done_logs)))
    def streak_for_habit(name):
        dates = sorted(set(map(lambda log : datetime.strptime(log["date"], "%Y-%m-%d").date(), filter(lambda log : log["habit_name"] == name, done_logs))))
        if not dates:
            return 0
        max_streak = 1
        current_streak = 1
        for i in range(1,len(dates)):
            if dates[i] ==dates[i-1] + timedelta(1):
                current_streak +=1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        return max_streak
    
    return dict(map(lambda name: (name, streak_for_habit(name)), habits_names))

def longuest_habit_streak_by_habit(habit_logs, habit_name):
    """
    Calculate the longest streak for a specific habit.

    Args:
        habit_logs (list[dict]): List of habit log dictionaries containing
            'habit_name', 'done', and 'date' keys.
        habit_name (str): Name of the habit to calculate the streak for.

    Returns:
        int: Longest consecutive streak for the specified habit.

    Example:
        >>> longuest_habit_streak_by_habit(logs, "Morning Run")
        7
    """
    done_logs = list(filter(lambda log: log["done"] == 1 and log["habit_name"] == habit_name, habit_logs))

    dates = sorted(set(map(lambda log : datetime.strptime(log["date"], "%Y-%m-%d").date(), filter(lambda log : log["habit_name"] == habit_name, done_logs))))
    if not dates:
        return 0
    max_streak = 1
    current_streak = 1
    for i in range(1,len(dates)):
        if dates[i] ==dates[i-1] + timedelta(1):
            current_streak +=1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1

    return max_streak
def group_habit_for_plot(habit_logs):
    """
    Group habit logs by habit name and sum completions for plotting.

    Args:
        habit_logs (list[dict]): List of habit log dictionaries containing
            'habit_name' and 'done' keys.

    Returns:
        pd.DataFrame: DataFrame with columns 'habit_name' and 'done'
            representing total completions per habit.

    Example:
        >>> df = group_habit_for_plot(logs)
    """
    df = pd.DataFrame(habit_logs)
    result = df.groupby("habit_name")["done"].sum().reset_index()
    return result
def habit_productivity_plot(habit_logs, habit_name):
    df = pd.DataFrame(habit_logs)
    df['date'] = pd.to_datetime(df['date']).dt.date
    #I want to do a plot who show the productivity like "you've done this habit % more this week " or less
def habit_most_productive_period():
    pass
def habit_most_productive_day(habit_logs, habit_name):
    """
    Find the most productive day of the week for a specific habit.

    Args:
        habit_logs (list[dict]): List of habit log dictionaries containing
            'habit_name', 'date', and 'done' keys.
        habit_name (str): Name of the habit to analyse.

    Returns:
        str: Name of the most productive day (e.g. 'Monday').

    Example:
        >>> habit_most_productive_day(logs, "Morning Run")
        'Monday'
    """
    filtered = list(filter(lambda log: log["habit_name"] == habit_name, habit_logs))
    df = pd.DataFrame(filtered)
    df["date"]= pd.to_datetime(df["date"]).dt.day_name()
    result = (df.groupby("date")["done"].sum().idxmax())
    
    return result
def habit_completion_rate(habit_logs, habit_name):
    """
    Calculate the completion rate for a specific habit.

    Args:
        habit_logs (list[dict]): List of habit log dictionaries containing
            'habit_name' and 'done' keys.
        habit_name (str): Name of the habit to analyse.

    Returns:
        tuple: A tuple containing done (int), not_done (int), rate (float).

    Example:
        >>> habit_completion_rate(logs, "Morning Run")
        (5, 2, 71.43)
    """
    filtered = list(filter(lambda log: log["habit_name"] == habit_name, habit_logs))
    return completion_rate(filtered)

#for category

def category_completion_rate(habit_logs, date):
    """
    Calculate the completion rate per category, with optional date filtering.

    Args:
        habit_logs (list[dict]): List of habit log dictionaries containing
            'category_name', 'done', and 'date' keys.
        date: Filtering option. Can be:
            - datetime.date: Filter for a specific day.
            - list[datetime.date]: Filter between date[0] and date[1].
            - None: No filtering, use all logs.

    Returns:
        pd.DataFrame: DataFrame with columns 'category_name', 'completed',
            'total', and 'completion_rate'.

    Example:
        >>> df = category_completion_rate(logs, date(2026, 3, 13))
    """
    filtered = habit_logs
    if isinstance(date, list):
        filtered = list(filter(lambda log: date[0] <= datetime.strptime(log["date"], "%Y-%m-%d").date() <= date[1], habit_logs))
    elif date:
        filtered =  list(filter(lambda log: datetime.strptime(log["date"], "%Y-%m-%d").date() == date, habit_logs))
    

    df = pd.DataFrame(filtered)
    if df.empty:
        return df

    result = df.groupby(df["category_name"])["done"].agg(completed = "sum", total ="count").reset_index()
    result["completion_rate"] = result["completed"]/result["total"]
    return result

def category_charts(habit_logs):
    """For best category, worst, top category etc"""
    df = pd.DataFrame(habit_logs)
    result = df.groupby(df["category_name"])["done"].agg(completed = "sum", total ="count").reset_index()

#per category
def category_completion_rate_per_category(habit_logs, category_name):
    """
    Calculate the completion rate for a specific category.

    Args:
        habit_logs (list[dict]): List of habit log dictionaries containing
            'category_name' and 'done' keys.
        category_name (str): Name of the category to analyse.

    Returns:
        pd.DataFrame: DataFrame with columns 'category_name', 'completed',
            'total', and 'completion_rate'.

    Example:
        >>> df = category_completion_rate_per_category(logs, "Health")
    """
    filtered = list(filter(lambda log: log["category_name"] == category_name, habit_logs))
    df = pd.DataFrame(filtered)
    if df.empty:
        return df
    result = df.groupby(df["category_name"])["done"].agg(completed = "sum", total ="count").reset_index()
    result["completion_rate"] = result["completed"]/result["total"]
    return result