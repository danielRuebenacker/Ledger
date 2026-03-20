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

