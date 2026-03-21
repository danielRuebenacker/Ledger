from django import forms
from django.contrib.auth.models import User
from ledger.models import UserProfile, HabitTracker, Habit
from tagify.fields import TagField

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('picture', )

class HabitTrackerForm(forms.Form):
    # TODO: have data_list call method that fetches top community habits
    dos = TagField(label='Must DOs', place_holder='Habit you want to DO everyday..', delimiters=' ', data_list=None)
    dos = TagField(label='Must NOT DOs', place_holder='Habit you want to NOT DO everyday..', delimiters=' ', data_list=None)
    easy_wins = TagField(label='Easy Wins', place_holder='Habits that motivate you to keep going..', delimiters=' ', data_list=None)
