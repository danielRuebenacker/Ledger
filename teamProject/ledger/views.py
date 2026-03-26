from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from ledger.models import UserProfile
from ledger.utils.habit_utils import get_all_months_data, create_habit, get_log_data, save_log
from datetime import date, datetime

# Create your views here.

def index(request):
    context_dict = {}

    return render(request, 'ledger/index.html', context=context_dict)

@login_required
def myhabits(request):
    context_dict = {}

    return render(request, 'ledger/myhabits.html', context=context_dict)

def leaderboards(request):
    context_dict = {}

    return render(request, 'ledger/leaderboards.html', context=context_dict)

def social(request):
    context_dict = {}

    return render(request, 'ledger/social.html', context=context_dict)

def profile(request):
    context_dict = {}

    return render(request, 'ledger/profile.html', context=context_dict)

@login_required
def myhabits_api(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    months = get_all_months_data(user_profile)
    return JsonResponse({'months': months})

@login_required
@require_POST
def create_habit_api(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    name = request.POST.get('name', '').strip()
    habit_type = request.POST.get('habit_type', '')

    habit, error = create_habit(name, habit_type, user_profile)
    if error:
        return JsonResponse({'error': error}, status=400)
    return JsonResponse({'success': True, 'name': habit.name})

@login_required
def log_habits_api(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    today = date.today()

    if request.method == 'GET':
        log_date_str = request.GET.get('date', today.isoformat())
        try:
            log_date = datetime.strptime(log_date_str, '%Y-%m-%d').date()
        except ValueError:
            log_date = today

        groups, journal_text, log_date = get_log_data(user_profile, log_date)
        return JsonResponse({
            'groups': groups,
            'journal': journal_text,
            'date': log_date.isoformat(),
        })

    # POST — save the log
    log_date_str = request.POST.get('date', today.isoformat())
    try:
        log_date = datetime.strptime(log_date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date.'}, status=400)

    checked_ids = request.POST.getlist('habits')
    journal_text = request.POST.get('journal', '').strip()

    error = save_log(user_profile, log_date, checked_ids, journal_text)
    if error:
        return JsonResponse({'error': error}, status=400)
    return JsonResponse({'success': True})

