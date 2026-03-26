from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from ledger.utils import date_utils, habit_utils

def user_profile_pic_path(instance, filename):
    import time
    ext = filename.split('.')[-1]
    return f'profile_images/user_{instance.user.id}_{int(time.time())}.{ext}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    picture = models.ImageField(upload_to=user_profile_pic_path, blank=True, default="guest.jpg")
    about_me = models.TextField(blank=True, default='')

    LIGHT = 'light'
    DARK = 'dark'
    THEME_CHOICES = ((LIGHT, 'Light'), (DARK, 'Dark'))
    
    # settings
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default=LIGHT)

    def __str__(self):
        return self.user.username


class Habit(models.Model):
    # say max length 25 chars (should be enough)
    name = models.CharField(max_length=25, blank=False, unique=True)

    is_community = models.BooleanField(default=False, blank=False)

    # enum choices
    TYPE_DO = "do"
    TYPE_DONT = "dont"
    TYPE_EASY_WIN = "easy_win"
    TYPE_NUMERIC = "numeric"
    HABIT_TYPE_CHOICES = (
            (TYPE_DO , "DO"),
            (TYPE_DONT , "DONT"),
            (TYPE_EASY_WIN , "EASY_WIN"),
            (TYPE_NUMERIC, "NUMERIC"),
    )
    habit_type = models.CharField(max_length=10, choices=HABIT_TYPE_CHOICES)
    # allows for easy habit creation with Habit.objects.create(..., type=Habit.TYPE_DO, ...)

    points = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'habit_type')
    
class Nudge(models.Model):
    nudger = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="sent_nudge")

    nudged = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="received_nudge")

    date_of_nudge = models.DateTimeField(auto_now_add=True)

    notified = models.BooleanField(default=False)

    def __str__(self):
        return f"User: {self.nudger} nudged User: {self.nudged} notified {self.notified}"
      
class FriendRequest(models.Model):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    STATUS_CHOICES = ((PENDING, "PENDING"), 
                      (ACCEPTED, "ACCEPTED"), 
                      (REJECTED, "REJECTED"), )
    
    requester = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="sent_friend_request")

    requested = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="received_friend_request")

    status = models.CharField(max_length=64, choices=STATUS_CHOICES, default=PENDING)

    date_accepted = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"User: {self.requester} requested User: {self.requested} currently {self.status}"

class Friendship(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="friends")
    friend = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="friend_of")

    def __str__(self):
        return f"{self.user} is friends with {self.friend}"


class HabitTracker(models.Model):
    # belongs to one user
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="habit_trackers")
    # this will be a MONTH field (set to 1st of month) (can only create habit trackers for THIS month (present))
    month = models.DateField(default=date_utils.get_first_of_this_month)
    # associated habits (M-N relationship)
    habits = models.ManyToManyField(Habit, related_name="habits")

    streak = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    
    class Meta:
        # tells django this combination must be unique
        unique_together = ("user", "month")

    def __str__(self):
        return self.user.user.username + self.month.strftime("%m-%Y")

    @property
    def is_streak_low(self):
        now = date_utils.now()
        if now.hour >= 18:
            day = self.days.filter(date=now.date()).first()

            # if not logged today or 
            if not day or not day.completed_on_day:
                return True
        return False

    def refresh_streak(self):
        self.streak = habit_utils.calculate_streak(self)
        self.save(update_fields=['streak'])


class Day(models.Model): 
    habit_tracker = models.ForeignKey(HabitTracker, on_delete=models.CASCADE, related_name="days")
    # specific day
    date = models.DateField()

    completed_on_day = models.BooleanField(default=False)

    class Meta:
        # tells django this combination must be unique
        unique_together = ("habit_tracker", "date")

class BoolHabitEntry(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name="bool_habit_entries")
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)

    done = models.BooleanField(default=False)

class JournalEntry(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    journal_text = models.TextField(blank=False)

    def __str__(self):
        return self.journal_text 
