from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    picture = models.ImageField(upload_to='profile_images', blank=True)
    
    about = models.TextField(blank=True)
    # other data to store defined here 
    # ...

    def __str__(self):
        return self.user.username


class Habit(models.Model):
    # say max length 25 chars (should be enough)
    name = models.CharField(max_length=25, blank=False)

    is_community = models.BooleanField(default=False, blank=False)

    # choices tuple (stand-in for enum)
    # Django 3.* has support for textChoices (enum) but since we are using 2.2.28
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
    type = models.CharField(max_length=10, choices=HABIT_TYPE_CHOICES)
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
