from django import forms
from django.contrib.auth.models import User
from ledger.models import UserProfile
from registration.forms import RegistrationForm

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('picture', )

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
