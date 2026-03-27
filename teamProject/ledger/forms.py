from django import forms
from django.contrib.auth.models import User
from ledger.models import UserProfile,  Habit, Day
from tagify.fields import TagField
from registration.forms import RegistrationForm
from ledger.utils.habit_utils import supply_form_with_popular_habits
from ledger.utils import date_utils, habit_utils

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('picture', )

class HabitTrackerForm(forms.Form):
    dos = TagField( label='Must DOs', place_holder='Habits you want to DO every day...', delimiters=',',)
    donts = TagField( label='Must NOT DOs', place_holder='Habits you want to NOT DO every day...', delimiters=',',)
    easy_wins = TagField( label='Easy Wins', place_holder='Habits that motivate you...', delimiters=',',)
    numeric = TagField( label='Numeric Habits', place_holder='E.g., Screentime, Liters of water', delimiters=',',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        type_map = {
            'dos': Habit.TYPE_DO,
            'donts': Habit.TYPE_DONT,
            'easy_wins': Habit.TYPE_EASY_WIN,
            'numeric': Habit.TYPE_NUMERIC,
        }

        for field_name, habit_type in type_map.items():
            try:
                popular = supply_form_with_popular_habits(habit_type)
                
                if popular:
                    self.fields[field_name].set_tag_args('data_list', popular)
            except Exception:
                # Fallback for migrations or empty DBs
                self.fields[field_name].set_tag_args('data_list', [])

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

class LogHabitForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=date_utils.today
    )
    journal_text = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'How was your day?'}),
        required=False
    )
    # dynamic habits -- add in init
    habits = forms.ModelMultipleChoiceField( queryset=Habit.objects.none(), widget=forms.CheckboxSelectMultiple, required=False)

    def __init__(self, *args, **kwargs):
        user_profile = kwargs.pop('user_profile', None)
        super().__init__(*args, **kwargs)
        
        if user_profile:
            tracker = habit_utils.get_current_month_habit_tracker(user_profile)
            if tracker:
                self.fields['habits'].queryset = tracker.habits.all()

class CreateHabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'habit_type']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. Drink Water'
            }),
            'habit_type': forms.Select(attrs={'class': 'form-select'}),
        }
