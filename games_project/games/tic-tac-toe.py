from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import random
import json
from .models import GameScore

def tic_tac_toe(request):
    return render(request, 'games/tic_tac_toe.html')

@csrf_exempt
def tic_tac_toe_move(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        board = data.get('board', [''] * 9)
        position = data.get('position')
        
        if board[position] == '':
            board[position] = 'X'
            
            winner = check_winner(board)
            if winner == 'X':
                player_name = data.get('player_name', 'Anonymous')
                GameScore.objects.create(
                    player_name=player_name,
                    game_type='tic_tac_toe',
                    score=100,
                    attempts=1
                )
                return JsonResponse({
                    'board': board,
                    'winner': 'X',
                    'message': 'You win!'
                })

            if '' not in board:
                return JsonResponse({
                    'board': board,
                    'winner': 'Draw',
                    'message': 'It\'s a draw!'
                })

            computer_move = get_computer_move(board)
            if computer_move is not None:
                board[computer_move] = 'O'

                winner = check_winner(board)
                if winner == 'O':
                    return JsonResponse({
                        'board': board,
                        'winner': 'O',
                        'message': 'Computer wins!'
                    })

                if '' not in board:
                    return JsonResponse({
                        'board': board,
                        'winner': 'Draw',
                        'message': 'It\'s a draw!'
                    })
        
        return JsonResponse({'board': board})

def check_winner(board):
    winning_combos = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  
        [0, 4, 8], [2, 4, 6]              
    ]
    
    for combo in winning_combos:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != '':
            return board[combo[0]]
    return None

def get_computer_move(board):
    for i in range(9):
        if board[i] == '':
            board[i] = 'O'
            if check_winner(board) == 'O':
                board[i] = '' 
                return i
            board[i] = ''
    
    for i in range(9):
        if board[i] == '':
            board[i] = 'X'
            if check_winner(board) == 'X':
                board[i] = ''  
                return i
            board[i] = ''

    if board[4] == '':
        return 4
    
    available = [i for i, spot in enumerate(board) if spot == '']
    return random.choice(available) if available else None
