from django.http import HttpResponse
from django.shortcuts import render
# from ledger.utils import habit_tracker
from ledger.forms import HabitTrackerForm

# Create your views here.

def index(request):
    context_dict = {}

    return render(request, 'ledger/index.html', context=context_dict)

def myhabits(request):
    context_dict = {}
    
    # if habit tracker is not created present form view
    if True:
        if request.method == 'POST':
            form = HabitTrackerForm(request.POST)

            if form.is_valid():
                dos = form.cleaned_data.get('dos')
                donts = form.cleaned_data.get('donts')
                easy_wins = form.cleaned_data.get('easy_wins')

                # make these into habits
                print(dos)
                print(donts)
                print(easy_wins)
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

