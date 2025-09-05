from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import random
import json
from .models import GameScore

def rock_paper_scissors(request):
    """Rock Paper Scissors game view"""
    if request.method == 'POST':
        player_choice = request.POST.get('choice')
        player_name = request.POST.get('player_name', 'Anonymous')
        
        choices = ['rock', 'paper', 'scissors']
        computer_choice = random.choice(choices)
        
        # Determine winner
        result = determine_rps_winner(player_choice, computer_choice)
        
        # Update session stats
        games_played = request.session.get('rps_games_played', 0) + 1
        wins = request.session.get('rps_wins', 0)
        
        if result == 'win':
            wins += 1
            score = 10
            GameScore.objects.create(
                player_name=player_name,
                game_type='rock_paper_scissors',
                score=score,
                attempts=games_played
            )
        
        request.session['rps_games_played'] = games_played
        request.session['rps_wins'] = wins
        
        context = {
            'player_choice': player_choice,
            'computer_choice': computer_choice,
            'result': result,
            'games_played': games_played,
            'wins': wins,
            'win_rate': round((wins / games_played) * 100, 1) if games_played > 0 else 0
        }
        
        return render(request, 'games/rock_paper_scissors.html', context)
    
    return render(request, 'games/rock_paper_scissors.html')

def determine_rps_winner(player, computer):
    """Determine winner of Rock Paper Scissors"""
    if player == computer:
        return 'tie'
    elif (player == 'rock' and computer == 'scissors') or \
         (player == 'paper' and computer == 'rock') or \
         (player == 'scissors' and computer == 'paper'):
        return 'win'
    else:
        return 'lose'

def reset_rps_stats(request):
    """Reset Rock Paper Scissors statistics"""
    request.session['rps_games_played'] = 0
    request.session['rps_wins'] = 0
    return redirect('rock_paper_scissors')