from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import random
import json
from .models import GameScore

def home(request):
    recent_scores = GameScore.objects.all()[:10]
    return render(request, 'games/home.html', {'recent_scores': recent_scores})
