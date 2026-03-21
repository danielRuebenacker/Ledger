from ledger.models import UserProfile, HabitTracker, Day, Habit, BoolHabitEntry
from ledger.utils import date

def get_user_habit_trackers(user):
    return list(user.habit_trackers.all().order_by('month'))

def get_current_month_habit_tracker(user):
    this_month = date.get_first_of_this_month()
    # get this months habit tracker
    try:
        habit_tracker = user.habit_trackers.get(month=this_month)
        return habit_tracker
    except HabitTracker.DoesNotExist:
        return None

def get_habit_tracker_habit_entries(habit_tracker):
    # this method takes a habit tracker and fetches all habit entries and organises them into a dict
    # by days. i.e. days is a dict of day keys to habit entry list values
    days = habit_tracker.days
    # stores collection of habit entries
    day_habits = {}
    for day in days:
        boolean_habit_entries = day.bool_habit_entries
        day_habits[day] = boolean_habit_entries
    return day_habits


def get_day(habit_tracker, date):
    # date is a datetime object
    try: 
        day = Day.objects.get(habit_tracker=habit_tracker, date=date)
        return day
    except Day.DoesNotExist:
        return None



def log_bool_habit(habit, user, done, date):
    # bool habit entry needs: day, habit, and done
    # date tracker is a datetime object
    # if we are logging it's got to be this month
    habit_tracker = get_current_month_habit_tracker(user)
    if habit_tracker is None: return
    day = get_day(habit_tracker=habit_tracker, date=date)
    if habit_tracker is None: return
    bool_habit_entry = BoolHabitEntry.objects.create(day=day, habit=habit, done=done)
    return bool_habit_entry

def calculate_streak(user):
    habit_tracker = get_current_month_habit_tracker(user)
    if habit_tracker is None: return
    # reverse ordering by date
    days = habit_tracker.days.order_by("-date")
    streak = 0
    for day in days:
        if not day.completed_on_the_day:
            return streak
        streak += 1
