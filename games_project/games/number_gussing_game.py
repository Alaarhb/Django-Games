from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import random
import json
from ..games.models import GameScore

def number_guess(request):
    if request.method == 'POST':
        guess = int(request.POST.get('guess', 0))
        target = request.session.get('target_number')
        attempts = request.session.get('attempts', 0) + 1
        
        if target is None:
            target = random.randint(1, 100)
            request.session['target_number'] = target
            attempts = 1
        
        request.session['attempts'] = attempts
        
        if guess == target:
            score = max(100 - attempts, 10)  
            player_name = request.POST.get('player_name', 'Anonymous')
            
            GameScore.objects.create(
                player_name=player_name,
                game_type='number_guess',
                score=score,
                attempts=attempts
            )
            
            messages.success(request, f'Congratulations! You guessed it in {attempts} attempts! Score: {score}')
            del request.session['target_number']
            del request.session['attempts']
            return redirect('number_guess')
        
        elif guess < target:
            hint = "Too low! Try a higher number."
        else:
            hint = "Too high! Try a lower number."
        
        return render(request, 'games/number_guess.html', {
            'hint': hint,
            'attempts': attempts,
            'guess': guess
        })
    
    if 'target_number' in request.session:
        del request.session['target_number']
    if 'attempts' in request.session:
        del request.session['attempts']
    
    return render(request, 'games/number_guess.html')