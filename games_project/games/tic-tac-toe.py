from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Count, Avg, Sum
from django.utils import timezone
import random
import json
from .models import Player, Game, GameScore, GameSession

def tic_tac_toe(request):
    """Enhanced Tic Tac Toe with DTL Variables"""
    game_obj = get_object_or_404(Game, name='tic_tac_toe')
    
    # Get statistics using DTL features
    game_stats = GameScore.objects.filter(game=game_obj).aggregate(
        total_games=Count('id'),
        avg_score=Avg('score'),
        wins=Count('id', filter= models.Q(score=100)),
        losses=Count('id', filter= models.Q(score=0))
    )
    
    recent_games = GameScore.objects.filter(game=game_obj).select_related('player')[:5]
    
    context = {
        'game': game_obj,
        'game_stats': game_stats,
        'recent_games': recent_games,
        'win_percentage': (game_stats['wins'] / game_stats['total_games'] * 100) if game_stats['total_games'] else 0,
    }
    
    return render(request, 'games/tic_tac_toe.html', context)

@csrf_exempt
def tic_tac_toe_move(request):
    """Handle Tic Tac Toe moves with enhanced logic"""
    if request.method == 'POST':
        data = json.loads(request.body)
        board = data.get('board', [''] * 9)
        position = data.get('position')
        player_name = data.get('player_name', 'Anonymous')
        
        # Get or create player
        player, created = Player.objects.get_or_create(
            name=player_name,
            defaults={'total_games': 0, 'total_score': 0}
        )
        
        game_obj = Game.objects.get(name='tic_tac_toe')
        
        # Player move
        if board[position] == '':
            board[position] = 'X'
            
            # Check if player wins
            winner = check_winner(board)
            if winner == 'X':
                # Player wins
                GameScore.objects.create(
                    player=player,
                    game=game_obj,
                    score=100,
                    attempts=1
                )
                player.total_games += 1
                player.total_score += 100
                player.save()
                
                return JsonResponse({
                    'board': board,
                    'winner': 'X',
                    'message': f'🎉 {player.name} wins! +100 points!'
                })
            
            # Check for draw
            if '' not in board:
                GameScore.objects.create(
                    player=player,
                    game=game_obj,
                    score=50,
                    attempts=1
                )
                player.total_games += 1
                player.total_score += 50
                player.save()
                
                return JsonResponse({
                    'board': board,
                    'winner': 'Draw',
                    'message': f'🤝 Draw! {player.name} gets 50 points!'
                })
            
            # Computer move
            computer_move = get_computer_move(board)
            if computer_move is not None:
                board[computer_move] = 'O'
                
                # Check if computer wins
                winner = check_winner(board)
                if winner == 'O':
                    GameScore.objects.create(
                        player=player,
                        game=game_obj,
                        score=0,
                        attempts=1
                    )
                    player.total_games += 1
                    player.save()
                    
                    return JsonResponse({
                        'board': board,
                        'winner': 'O',
                        'message': f'💔 Computer wins! Better luck next time, {player.name}!'
                    })
                
                # Check for draw after computer move
                if '' not in board:
                    GameScore.objects.create(
                        player=player,
                        game=game_obj,
                        score=50,
                        attempts=1
                    )
                    player.total_games += 1
                    player.total_score += 50
                    player.save()
                    
                    return JsonResponse({
                        'board': board,
                        'winner': 'Draw',
                        'message': f'🤝 Draw! {player.name} gets 50 points!'
                    })
        
        return JsonResponse({'board': board})

def check_winner(board):
    """Check if there's a winner in Tic Tac Toe"""
    winning_combos = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]
    
    for combo in winning_combos:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != '':
            return board[combo[0]]
    return None

def get_computer_move(board):
    """Enhanced AI for Tic Tac Toe"""
    # Try to win
    for i in range(9):
        if board[i] == '':
            board[i] = 'O'
            if check_winner(board) == 'O':
                board[i] = ''
                return i
            board[i] = ''
    
    # Try to block player
    for i in range(9):
        if board[i] == '':
            board[i] = 'X'
            if check_winner(board) == 'X':
                board[i] = ''
                return i
            board[i] = ''
    
    # Take center if available
    if board[4] == '':
        return 4
    
    # Take corners
    corners = [0, 2, 6, 8]
    available_corners = [i for i in corners if board[i] == '']
    if available_corners:
        return random.choice(available_corners)
    
    # Take any available spot
    available = [i for i, spot in enumerate(board) if spot == '']
    return random.choice(available) if available else None
