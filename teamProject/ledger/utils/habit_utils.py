from ledger.models import UserProfile, HabitTracker, DayTracker, Habit, BoolHabitEntry
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
    day_trackers = habit_tracker.day_trackers
    # stores collection of habit entries
    days = {}
    for day_tracker in day_trackers:
        boolean_habit_entries = day_tracker.bool_habit_entries
        days[day_tracker] = boolean_habit_entries
    return days


def get_day_tracker(habit_tracker, date):
    # date is a datetime object
    try: 
        day_tracker = DayTracker.objects.get(habit_tracker=habit_tracker, date=date)
        return day_tracker
    except DayTracker.DoesNotExist:
        return None



def log_bool_habit(habit, user, done, date):
    # bool habit entry needs: day_tracker, habit, and done
    # date tracker is a datetime object
    # if we are logging it's got to be this month
    habit_tracker = get_current_month_habit_tracker(user)
    if habit_tracker is None: return
    day_tracker = get_day_tracker(habit_tracker=habit_tracker, date=date)
    if habit_tracker is None: return
    bool_habit_entry = BoolHabitEntry.objects.create(day_tracker=day_tracker, habit=habit, done=done)
    return bool_habit_entry
