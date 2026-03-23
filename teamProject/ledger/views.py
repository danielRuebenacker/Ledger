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
    # if habit tracker is not created present form view
    habit_tracker, created = HabitTracker.objects.get_or_create(user=user_profile, month=date.get_first_of_this_month())
    
    # newly created
    if created:
        if request.method == 'POST':
            form = HabitTrackerForm(request.POST)

            if form.is_valid():
                # ignore empty strings
                dos_strings = [h for h in form.cleaned_data.get('dos') if h]
                donts_strings = [h for h in form.cleaned_data.get('donts') if h]
                easy_wins_strings = [h for h in form.cleaned_data.get('easy_wins') if h] 

                # makes into habits/gets habit then adds to habit tracker
                habit_utils.get_or_create_habits_then_register(dos_strings, donts_strings, easy_wins_strings, habit_tracker)

                return redirect('myhabits.html')
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

