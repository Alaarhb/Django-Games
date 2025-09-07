from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Count, Avg, Sum
from django.utils import timezone
import random
import json
from .models import Player, Game, GameScore, GameSession

def home(request):
    """Home page with comprehensive game statistics using DTL"""
    # Using DTL Variables
    games = Game.objects.filter(is_active=True)
    recent_scores = GameScore.objects.select_related('player', 'game')[:10]
    top_players = Player.objects.annotate(
        games_count=Count('scores')
    ).filter(games_count__gt=0)[:5]
    
    # Statistics for DTL
    total_games_played = GameScore.objects.count()
    total_players = Player.objects.count()
    
    # Using DTL Filters in context
    context = {
        'games': games,
        'recent_scores': recent_scores,
        'top_players': top_players,
        'total_games_played': total_games_played,
        'total_players': total_players,
        'current_time': timezone.now(),
    }
    
    return render(request, 'games/home.html', context)
