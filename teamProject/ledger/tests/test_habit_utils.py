from django.shortcuts import reverse
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

    def test_get_day(self):
        # given a day (datetime) and a habit tracker return day
        today = date.today()
        day = DayFactory(date=today)
        # subfactory created habit_tracke
        habit_tracker = day.habit_tracker
        util_day = habit_utils.get_day(habit_tracker=habit_tracker, date=today)
        self.assertEquals(day, util_day)

    def test_log_entry(self):
        # given habit, user, day, and done log habit
        day = DayFactory()
        date = day.date
        habit = HabitFactory()

        # these shenanigans are for getting the user
        habit_tracker = day.habit_tracker
        user = habit_tracker.user

        # now test whether actual entry is the same as the one created by utils
        util_bool_habit_entry = habit_utils.log_bool_habit(habit=habit, user=user, date=date, done=True)
        bool_habit_entry = BoolHabitEntry.objects.get(day=day, habit=habit)
        self.assertEquals(bool_habit_entry, util_bool_habit_entry)

    def test_register_habits_with_habit_tracker(self):
        habit1 = HabitFactory()
        habit2 = HabitFactory()
        habit3 = HabitFactory()
        habit_list = [habit1, habit2, habit3]
        

        habit_tracker = HabitTrackerFactory()
        habit_utils.register_habits_with_habit_tracker(habit_list, habit_tracker)
        habit_list_query = list(habit_tracker.habits.all())
        self.assertEquals(habit_list, habit_list_query)


class TestHabitTrackerForm(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        self.profile = UserProfileFactory(user=self.user)

        self.client.login(username="test", password="test")

    def test_full_habit_tracker_creation(self):
        url = reverse('ledger:myhabits')

        habits_dict = {
            'dos': 'read, bed before 12',
            'donts': 'caffeine', 
            'easy_wins': 'go outside, drink water',
            'numeric': 'screentime, hours of sleep',
        }
        NUM_HABITS = 7 
        response = self.client.post(url, habits_dict)

        # 302: redirect
        self.assertEqual(response.status_code, 302)

        habit_tracker = habit_utils.get_current_month_habit_tracker(self.profile)

        # 5 habits 
        self.assertEqual(Habit.objects.count(), NUM_HABITS)

        # check exist
        read = Habit.objects.filter(name='read')
        caffeine = Habit.objects.filter(name='caffeine')
        hours_of_sleep = Habit.objects.filter(name='hours of sleep')
        self.assertTrue(read.exists())
        self.assertTrue(caffeine.exists())
        self.assertTrue(hours_of_sleep.exists())

        # check correct type
        self.assertEquals(read.first().habit_type, Habit.TYPE_DO)
        self.assertEquals(caffeine.first().habit_type, Habit.TYPE_DONT)
        self.assertEquals(hours_of_sleep.first().habit_type, Habit.TYPE_NUMERIC)


        # many to many habit count
        self.assertEquals(habit_tracker.habits.count(), NUM_HABITS)

