from django.shortcuts import redirect, render
from ledger.utils import habit_utils, date
from ledger.forms import HabitTrackerForm
from ledger.models import HabitTracker

# Create your views here.

def index(request):
    context_dict = {}

    return render(request, 'ledger/index.html', context=context_dict)

def myhabits(request):
    context_dict = {}
    user_profile = request.user.userprofile
    new_signup = True
    # if habit tracker is not created present form view
    habit_tracker, created = HabitTracker.objects.get_or_create(user=user_profile, month=date.get_first_of_this_month())
    if not created:
        new_signup = False
    
    if request.method == 'POST':
        form = HabitTrackerForm(request.POST)

        if form.is_valid():
            # ignore empty strings
            clean = lambda x: x.strip().lower()

            # get all cleaned data, and clean according to our clean
            habit_string_lists = [
                    [clean(h) for h in form.cleaned_data.get(f, []) if h] 
                    for f in ('dos', 'donts', 'easy_wins', 'numeric')
            ]

            # makes into habits/gets habit then adds to habit tracker
            habit_utils.get_or_create_habits_then_register(*habit_string_lists, habit_tracker)

            new_signup = False
            return redirect('ledger:myhabits')
    else:
        if new_signup: 
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

