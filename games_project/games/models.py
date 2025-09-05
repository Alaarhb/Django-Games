from django.db import models
from django.contrib.auth.models import User

class GameScore(models.Model):
    GAME_CHOICES = [
        ('number_guess', 'Number Guessing'),
        ('tic_tac_toe', 'Tic Tac Toe'),
        ('rock_paper_scissors', 'Rock Paper Scissors'),
    ]
    
    player_name = models.CharField(max_length=100)
    game_type = models.CharField(max_length=20, choices=GAME_CHOICES)
    score = models.IntegerField()
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.player_name} - {self.game_type}: {self.score}"
    
    class Meta:
        ordering = ['-score', '-created_at']