from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def index(request):
    context_dict = {}
    return render(request, 'ledger/index.html', context=context_dict)

def myhabits(request):
    context_dict = {}
    return render(request, 'ledger/myhabits.html', context=context_dict)

def leaderboards(request):
    context_dict = {}
    return render(request, 'ledger/leaderboards.html', context=context_dict)

def social(request):
    context_dict = {}
    return render(request, 'ledger/social.html', context=context_dict)

def friends(request):
    context_dict = {
        'friends_list': [
            {'name': 'Alice', 'streak': 12, 'points': 340},
            {'name': 'Ben', 'streak': 8, 'points': 210},
            {'name': 'Chloe', 'streak': 15, 'points': 410},
        ]
    }
    return render(request, 'ledger/friends.html', context=context_dict)

def requests_page(request):
    incoming_requests = [
        {'name': 'Emma'},
        {'name': 'Jack'},
    ]

    sent_requests = [
        {'name': 'Olivia'},
        {'name': 'Noah'},
    ]

    action = request.GET.get('action', '').strip()
    user = request.GET.get('user', '').strip()

    message = ''
    if action == 'accept' and user:
        message = f'Friend request from {user} accepted.'
        incoming_requests = [req for req in incoming_requests if req['name'] != user]
    elif action == 'reject' and user:
        message = f'Friend request from {user} rejected.'
        incoming_requests = [req for req in incoming_requests if req['name'] != user]

    context_dict = {
        'incoming_requests': incoming_requests,
        'sent_requests': sent_requests,
        'message': message,
    }
    return render(request, 'ledger/requests.html', context=context_dict)

def search_users(request):
    all_users = [
        {'name': 'Liam'},
        {'name': 'Sophia'},
        {'name': 'Mason'},
        {'name': 'Isabella'},
    ]

    query = request.GET.get('q', '').strip()
    added_user = request.GET.get('added', '').strip()

    if query:
        search_results = [
            user for user in all_users
            if query.lower() in user['name'].lower()
        ]
    else:
        search_results = all_users

    context_dict = {
        'search_results': search_results,
        'query': query,
        'added_user': added_user,
    }
    return render(request, 'ledger/search.html', context=context_dict)

def nudge_page(request):
    friends_list = [
        {'name': 'Alice'},
        {'name': 'Ben'},
        {'name': 'Chloe'},
    ]

    sent_to = request.GET.get('sent_to', '').strip()
    message_text = request.GET.get('message', '').strip()

    success_message = ''
    error_message = ''

    if 'sent_to' in request.GET or 'message' in request.GET:
        if not sent_to:
            error_message = 'Please select a friend before sending a nudge.'
        else:
            success_message = f'Nudge sent to {sent_to}.'
            message_text = ''

    context_dict = {
        'friends_list': friends_list,
        'sent_to': sent_to,
        'message_text': message_text,
        'success_message': success_message,
        'error_message': error_message,
    }
    return render(request, 'ledger/nudge.html', context=context_dict)