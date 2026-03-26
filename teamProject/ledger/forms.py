from django import forms
from django.contrib.auth.models import User
from ledger.models import UserProfile, HabitTracker, Habit
from tagify.fields import TagField
from registration.forms import RegistrationForm

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('picture', )

class HabitTrackerForm(forms.Form):
    # TODO: have data_list call method that fetches top community habits
    dos = TagField(label='Must DOs', place_holder='Habit you want to DO everyday..', delimiters=',', data_list=None)
    donts = TagField(label='Must NOT DOs', place_holder='Habit you want to NOT DO everyday..', delimiters=',', data_list=None)
    easy_wins = TagField(label='Easy Wins', place_holder='Habits that motivate you to keep going..', delimiters=',', data_list=None)
    numeric = TagField(label='Numeric Habits', place_holder='E.g. Screentime', delimiters=',', data_list=None)

class CustomRegistrationForm(RegistrationForm): 
    theme = forms.ChoiceField(
        choices=UserProfile.THEME_CHOICES, 
        initial=UserProfile.LIGHT
    )
    picture = forms.ImageField(required=False, label="Profile Picture")

    def save(self, commit=True):
        user = super().save(commit=commit)

        profile_data = {
            'user': user,
            'theme': self.cleaned_data.get('theme', UserProfile.LIGHT),
            'about_me': ''
        }

        if self.cleaned_data.get('picture'):
            profile_data['picture'] = self.cleaned_data.get('picture')
        UserProfile.objects.create(**profile_data)
        return user
