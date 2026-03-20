from django.test import TestCase
from ledger.utils import habit_utils, date
from .test_factories import *
from datetime import datetime

class TestHabitTrackerGet(TestCase):
    def test_get_habit_tracker(self):
        habit_tracker = HabitTrackerFactory()
        user = habit_tracker.user
        util_habit_tracker = habit_utils.get_current_month_habit_tracker(user=user)
        self.assertEquals(habit_tracker, util_habit_tracker)

    def test_get_all_user_habit_trackers(self):
        user = UserProfileFactory()
        feb = date.get_first_of_n_months_ago(1)
        jan = date.get_first_of_n_months_ago(2)
        dec = date.get_first_of_n_months_ago(3)
        nov = date.get_first_of_n_months_ago(4)

        _ = HabitTrackerFactory(user=user, month=feb)
        _ = HabitTrackerFactory(user=user, month=jan)
        _ = HabitTrackerFactory(user=user, month=dec)
        _ = HabitTrackerFactory(user=user, month=nov)
        habit_trackers = habit_utils.get_user_habit_trackers(user=user)
        # self.assertEquals(habit_trackers, list(user.habit_trackers.all().order_by('month')))
        self.assertEquals(len(habit_trackers), user.habit_trackers.all().count())

    def test_get_this_month_user_habit_trackers(self):
        user = UserProfileFactory()
        this_month = date.get_first_of_this_month()
        habit_tracker = HabitTrackerFactory(user=user, month=this_month)
        util_habit_tracker = habit_utils.get_current_month_habit_tracker(user=user)
        self.assertEquals(habit_tracker, util_habit_tracker)

    def test_get_day_tracker(self):
        # given a day (datetime) and a habit tracker return day_tracker
        today = date.today()
        day_tracker = DayTrackerFactory(date=today)
        # subfactory created habit_tracke
        habit_tracker = day_tracker.habit_tracker
        util_day_tracker = habit_utils.get_day_tracker(habit_tracker=habit_tracker, date=today)
        self.assertEquals(day_tracker, util_day_tracker)

    def test_log_entry(self):
        # given habit, user, day, and done log habit
        day_tracker = DayTrackerFactory()
        date = day_tracker.date
        habit = HabitFactory()

        # these shenanigans are for getting the user
        habit_tracker = day_tracker.habit_tracker
        user = habit_tracker.user

        # now test whether actual entry is the same as the one created by utils
        util_bool_habit_entry = habit_utils.log_bool_habit(habit=habit, user=user, date=date, done=True)
        bool_habit_entry = BoolHabitEntry.objects.get(day_tracker=day_tracker, habit=habit)
        self.assertEquals(bool_habit_entry, util_bool_habit_entry)
        

