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