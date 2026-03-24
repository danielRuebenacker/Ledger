import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teamProject.settings')

import django
django.setup()
from ledger.models import UserProfile, Habit, Nudge, Friendship, HabitTracker, DayTracker, BoolHabitEntry, JournalEntry
from django.contrib.auth.models import User
import random
from datetime import datetime
from datetime import timedelta
from ledger.tests.test_factories import get_first_of_month

def populate_users():
    names = ["Jones", "Smith", "Miller", "Davis", "David", "Wilson", "Johnson", "Taylor", "Kelly", "Madison", "Parker"]

    for nameZero in names:
        for name in names:
            if name != nameZero:
                username = f"{name}_{nameZero}"
                email = f"{name}_{nameZero}@fake.com"
                password = 'password123'
                add_user(username, email, password)

def populate_habits():
    habits = []
    point1 = 1
    point2 = 2
    point3 = 3
    habit1 = {"name": "Read", "is_community": False, "habit_type": "TYPE_DO", "points": point2}
    habit2 = {"name": "Walk", "is_community": False, "habit_type": "TYPE_DO", "points": point2}
    habit3 = {"name": "Phone before bed", "is_community": False, "habit_type": "TYPE_DONT", "points": point2}
    
    habit4 = {"name": "Study", "is_community": False, "habit_type": "TYPE_DO", "points": point2}
    habit5 = {"name": "Caffeine", "is_community": False, "habit_type": "TYPE_DONT", "points": point3}
    habit6 = {"name": "Go outside", "is_community": False, "habit_type": "TYPE_EASY_WIN", "points": point1}
    
    habit7 = {"name": "Listen to music", "is_community": False, "habit_type": "TYPE_EASY_WIN", "points": point1}
    habit8 = {"name": "Coffee", "is_community": False, "habit_type": "TYPE_EASY_WIN", "points": point1}
    habit9 = {"name": "Phone someone", "is_community": False, "habit_type": "TYPE_EASY_WIN", "points": point1}
    
    habit10 = {"name": "Gym", "is_community": False, "habit_type": "TYPE_DO", "points": point2}
    habit11 = {"name": "Doomscroll", "is_community": False, "habit_type": "TYPE_DONT", "points": point3}
    habit12 = {"name": "Journal", "is_community": False, "habit_type": "TYPE_DO", "points": point2}

    habits.append(habit1)
    habits.append(habit2)
    habits.append(habit3)
    habits.append(habit4)
    habits.append(habit5)
    habits.append(habit6)
    habits.append(habit7)
    habits.append(habit8)
    habits.append(habit9)
    habits.append(habit10)
    habits.append(habit11)
    habits.append(habit12)

    for habit in habits:
        add_habit(name=habit["name"], is_community=habit["is_community"], habit_type=habit["habit_type"], points=habit["points"])

def populate_friendship():
    users = list(UserProfile.objects.all())
    p = 100 - random.randint(60, 80)

    for i in range(len(users)):
         for j in range(len(users)):
             if i < j:
                 rand = random.randint(0, 100)
                 if rand < p:
                     random_time = random.randint(0, 21)
                     add_Friendship(users[i], users[j], status="ACCEPTED", date_accepted=datetime.today() - timedelta(random_time) )    

def populate_trackers():
    users = list(UserProfile.objects.all())
    habits = list(Habit.objects.all())
    
    for user in users:
        p_of_habit = random.randint(20, 50)
        user_habits = []
        for habit in habits:
            p_habit = random.randint(0, 100)
            if p_habit < p_of_habit:
                user_habits.append(habits)
        tracker = add_habit_tracker(user, get_first_of_month(), user_habits)
        range_random = random.randint(3, 7)
        day_trackers = []
        for time_delta in range(range_random):
            day_trackers.append(add_day_tracker(tracker, datetime.today() - timedelta(time_delta), True))
        for day_tracker in day_trackers:
            bool_habit_entry(day_tracker, tracker , True)
            add_journal_entry(day_tracker)
        

def add_user(username, email, password):
    userDjango = User.objects.create_user(username=username, email=email, password=password)
    user = UserProfile.objects.get_or_create(user=userDjango)[0]
    user.save()
    return user

def add_habit(name, is_community, habit_type, points):
    habit = Habit.objects.get_or_create(name=name, is_community=is_community, habit_type=habit_type, points=points)[0]
    habit.save()
    return habit 

def add_Nudge(nudger, nudged, date_of_nudge, notified):
    nudge = Nudge.objects.get_or_create(nudger=nudger, nudged=nudged, date_of_nudge=date_of_nudge, notified=notified)[0]
    nudge.save()
    return nudge

def add_Friendship(requester, requested, status, date_accepted):
    friendship = Friendship.objects.get_or_create(requester=requester, requested=requested, status=status, date_accepted=date_accepted)[0]
    friendship.save()
    return friendship

def add_habit_tracker(user, month, habits):
    habit_tracker = HabitTracker.objects.get_or_create(user=user, month=month)[0]
    habit_tracker.save()
    for habit in habits:
        habit_tracker.habits.add(habit)
    return habit_tracker

def add_day_tracker(tracker, date, completed_on_day):
    day_tracker = DayTracker.objects.get_or_create(tracker=tracker, date=date, completed_on_day=completed_on_day)[0]
    day_tracker.save()
    return day_tracker

def bool_habit_entry(day_tracker, habit, done):
    bool_habit_entry = BoolHabitEntry.objects.get_or_create(day_tracker=day_tracker, habit=habit, done=done)[0]
    bool_habit_entry.save()
    return bool_habit_entry

def add_journal_entry(day_tracker, journal_text="Today I wrote something in my Journal"):
    journal_entry = JournalEntry.objects.get_or_create(day_tracker=day_tracker, journal_text=journal_text)[0]
    journal_entry.save()
    return journal_entry

if __name__ == '__main__':
    User.objects.all().delete()
    Habit.objects.all().delete()

    populate_users()
    print("POP USERS")

    populate_habits()
    print("POP HABITS")

    populate_friendship()
    print("POP FREINDS")

    populate_trackers()
    print("POP TRACKERS")