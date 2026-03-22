from django.http import HttpResponse
from django.shortcuts import render
from ledger.utils import habit_utils
from ledger.forms import HabitTrackerForm
from ledger.models import Habit

# Create your views here.

def index(request):
    context_dict = {}

    return render(request, 'ledger/index.html', context=context_dict)

def myhabits(request):
    context_dict = {}
    user_profile = request.user.userprofile
    # if habit tracker is not created present form view
    habit_tracker = habit_utils.get_current_month_habit_tracker(user_profile)
    
    if not habit_tracker:
        # create one
        if request.method == 'POST':
            form = HabitTrackerForm(request.POST)

            if form.is_valid():
                # ignore empty strings
                dos_strings = [h for h in form.cleaned_data.get('dos') if h]
                donts_strings = [h for h in form.cleaned_data.get('donts') if h]
                easy_wins_strings = [h for h in form.cleaned_data.get('easy_wins') if h] 

                # make these into habits
                dos = habit_utils.get_or_create_habits_from_list(dos_strings, Habit.TYPE_DO)
                donts = habit_utils.get_or_create_habits_from_list(donts_strings, Habit.TYPE_DONT)
                easy_wins = habit_utils.get_or_create_habits_from_list(easy_wins_strings, Habit.TYPE_EASY_WIN)

        else:
            form = HabitTrackerForm()

        context_dict['form'] = form
        return render(request, 'ledger/create_habit_tracker.html', context=context_dict)
    else:
        return render(request, 'ledger/myhabits.html', context=context_dict)



def leaderboards(request):
    context_dict = {}

    return render(request, 'ledger/myhabits.html', context=context_dict)

def social(request):
    context_dict = {}

    return render(request, 'ledger/social.html', context=context_dict)

def profile(request):
    context_dict = {}

    return render(request, 'ledger/profile.html', context=context_dict)

