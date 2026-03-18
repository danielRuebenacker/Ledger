from ledger.models import UserProfile, HabitTracker, Habit, BoolHabitEntry
from ledger.utils import date

def get_user_habit_trackers(user):
    return user.habit_trackers.all()

def get_current_month_habit_tracker(user):
    this_month = date.get_first_of_this_month()
    # get this months habit tracker
    try:
        habit_tracker = HabitTracker.objects.get(month=this_month)
        return habit_tracker
    except HabitTracker.DoesNotExist:
        return none

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



def log_boolean_habit(habit, user, done):
    bool_habit_entry = BoolHabitEntry.objects.create(user=user, habit=habit, done=done)
