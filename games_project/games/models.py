from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Player(models.Model):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_games = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
    
    @property
    def average_score(self):
        return self.total_score / self.total_games if self.total_games > 0 else 0
    
    class Meta:
        ordering = ['-total_score', 'name']

class Game(models.Model):
    GAME_TYPES = [
        ('number_guess', 'Number Guessing Game'),
        ('tic_tac_toe', 'Tic Tac Toe'),
        ('rock_paper_scissors', 'Rock Paper Scissors'),
    ]
    
    name = models.CharField(max_length=50, choices=GAME_TYPES, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=10, default='🎮')
    max_score = models.IntegerField(default=100)
    difficulty_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
        default=3
    )
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.get_name_display()

class GameScore(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='scores')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='scores')
    score = models.IntegerField()
    attempts = models.IntegerField(default=1)
    duration = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.player.name} - {self.game.name}: {self.score}"
    
    class Meta:
        ordering = ['-score', '-created_at']

class GameSession(models.Model):
    SESSION_STATUS = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='active')
    current_data = models.JSONField(default=dict)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.player.name} - {self.game.name} ({self.status})"
