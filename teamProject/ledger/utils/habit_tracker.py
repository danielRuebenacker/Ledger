from ledger.models import UserProfile, HabitTracker, Habit, BoolHabitEntry
import datetime

def get_user_habit_trackers(user):
    return user.habit_trackers

def get_current_month_habit_tracker(user):
    # get this months habit tracker
    habit_tracker = 

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

def get_user_day_tracker_today(user):
    this_month_ht = 


def log_boolean_habit(habit, user):
    bool_habit_entry = BoolHabitEntry()
