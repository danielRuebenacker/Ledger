from django.db import models
from django.contrib.auth.models import User

def user_profile_pic_path(instance, filename):
    import time
    ext = filename.split('.')[-1]
    return f'profile_images/user_{instance.user.id}_{int(time.time())}.{ext}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    picture = models.ImageField(upload_to=user_profile_pic_path, blank=True)
    about_me = models.TextField(blank=True, default='')
    LIGHT = 'light'
    DARK = 'dark'
    THEME_CHOICES = ((LIGHT, 'Light'), (DARK, 'Dark'))
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default=LIGHT)
    # other data to store defined here 
    # ...

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
    
class Nudge(models.Model):
    nudger = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="sent_nudge")

    nudged = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="received_nudge")

    date_of_nudge = models.DateTimeField(auto_now_add=True)

    notified = models.BooleanField(default=False)

    def __str__(self):
        return f"User: {self.nudger} nudged User: {self.nudged} notified {self.notified}"
      
class Friendship(models.Model):
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

class HabitTracker(models.Model):
    # belongs to one user
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    # this will be a MONTH field (set to 1st of month)
    month = models.DateField();
    # associated habits (M-N relationship)
    habits = models.ManyToManyField(Habit)

    class Meta:
        # tells django this combination must be unique
        unique_together = ("user", "month")

    def __str__(self):
        return self.user.user.username + self.month.strftime("%m-%Y")

class DayTracker(models.Model): 
    tracker = models.ForeignKey(HabitTracker, on_delete=models.CASCADE)
    # specific day
    date = models.DateField()

    completed_on_day = models.BooleanField(default=False)

    class Meta:
        # tells django this combination must be unique
        unique_together = ("tracker", "date")

class BoolHabitEntry(models.Model):
    day_tracker = models.ForeignKey(DayTracker, on_delete=models.CASCADE)
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)

    done = models.BooleanField(default=False);
