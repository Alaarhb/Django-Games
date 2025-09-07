from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Count, Avg, Sum
from django.utils import timezone
import random
import json
from .models import Player, Game, GameScore, GameSession

def number_guess(request):
    """Enhanced Number Guessing Game with DTL Variables and Filters"""
    game_obj = get_object_or_404(Game, name='number_guess')
    
    if request.method == 'POST':
        player_name = request.POST.get('player_name', 'Anonymous')
        guess = int(request.POST.get('guess', 0))
        
        # Get or create player using DTL Variables
        player, created = Player.objects.get_or_create(
            name=player_name,
            defaults={'total_games': 0, 'total_score': 0}
        )
        
        target = request.session.get('target_number')
        attempts = request.session.get('attempts', 0) + 1
        start_time = request.session.get('game_start_time')
        
        if target is None:
            target = random.randint(1, 100)
            request.session['target_number'] = target
            request.session['game_start_time'] = timezone.now().isoformat()
            attempts = 1
        
        request.session['attempts'] = attempts
        
        if guess == target:
            # Game completed - calculate score using DTL logic
            score = max(100 - attempts, 10)
            
            # Save score
            GameScore.objects.create(
                player=player,
                game=game_obj,
                score=score,
                attempts=attempts
            )
            
            # Update player statistics
            player.total_games += 1
            player.total_score += score
            player.save()
            
            messages.success(
                request, 
                f'🎉 Congratulations {player.name}! You guessed {target} in {attempts} attempts! Score: {score}'
            )
            
            # Clear session
            for key in ['target_number', 'attempts', 'game_start_time']:
                if key in request.session:
                    del request.session[key]
            
            return redirect('number_guess')
        
        else:
            hint = "Too low! Try higher." if guess < target else "Too high! Try lower."
            
            context = {
                'game': game_obj,
                'hint': hint,
                'attempts': attempts,
                'guess': guess,
                'player_name': player_name,
                'progress_percentage': min((attempts / 20) * 100, 100),
            }
            return render(request, 'games/number_guess.html', context)
    
    # GET request - show game with statistics using DTL
    player_scores = GameScore.objects.filter(game=game_obj).select_related('player')[:5]
    best_score = player_scores.first() if player_scores else None
    
    context = {
        'game': game_obj,
        'player_scores': player_scores,
        'best_score': best_score,
        'total_attempts': GameScore.objects.filter(game=game_obj).count(),
    }
    
    return render(request, 'games/number_guess.html', context)
