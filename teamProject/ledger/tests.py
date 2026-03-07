from django.test import TestCase

# ---------- models -----------
from django.contrib.auth.models import User
from ledger.models import Habit, HabitTracker
from ledger.models import UserProfile

# --------- misc -------------
from datetime import datetime

def create_habit(name, habit_type, is_community, points):
        habit = Habit(name=name, habit_type=habit_type, is_community=is_community, points=points)
        habit.save()
        return habit

def create_test_user():
    # base user object
    user = User.objects.create_user(username='test', password='test')

    userProfile = UserProfile(user=user)
    userProfile.save()
    return userProfile

def get_first_of_this_month():
    td = datetime.today()
    first = td.replace(day=1)
    return first

class HabitTests(TestCase):
    def test_create_habit(self):
        create_habit("Read", Habit.TYPE_DO, True, 10)
        self.assertTrue(Habit.objects.exists())

class HabitTrackerTests(TestCase):
    def test_create_HabitTracker(self):
        habit = create_habit("Read", Habit.TYPE_DO, True, 10)
        user = create_test_user()
        first = get_first_of_this_month()
        
        tracker = HabitTracker(user=user, month=first)
        # before adding habits need to do
        tracker.save()
        # now can add
        tracker.habits.add(habit)

        self.assertTrue(HabitTracker.objects.exists())

