from django.test import TestCase
from ledger.utils import date_utils

class TestDate(TestCase):
    def test_get_last_month(self):
        first_of_last = date_utils.get_first_of_n_months_ago(1)
        # obviously dependent on today being in March...
        self.assertEquals("Feb", first_of_last.strftime("%b"))

    def test_get_4_months_ago(self):
        first_of_last = date_utils.get_first_of_n_months_ago(3)
        # again dependent on today's date
        self.assertEquals("Dec", first_of_last.strftime("%b"))
        self.assertEquals("2025", first_of_last.strftime("%Y"))

