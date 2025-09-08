from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db.models import Q, Avg, Count, Sum, Max, Min
from django.urls import reverse
import uuid
from datetime import timedelta

class TimestampedModel(models.Model):
    """Abstract base model with created and updated timestamps"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Category(TimestampedModel):
    """Game categories for organization"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default='🎮')
    color = models.CharField(
        max_length=7,
        default='#667eea',
        validators=[RegexValidator(r'^#[0-9A-Fa-f]{6}$', 'Enter valid hex color')]
    )
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

class Player(TimestampedModel):
    """Enhanced Player model with detailed statistics"""
    # Basic Information
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(blank=True, null=True)
    avatar = models.CharField(max_length=10, default='🎮')
    
    # Statistics
    total_games = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    highest_score = models.IntegerField(default=0)
    total_playtime = models.DurationField(default=timedelta(0))
    
    # Preferences
    preferred_difficulty = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    favorite_category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    last_played = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    @property
    def average_score(self):
        """Calculate average score per game"""
        return round(self.total_score / self.total_games, 2) if self.total_games > 0 else 0
    
    @property
    def rank(self):
        """Get player ranking based on total score"""
        return Player.objects.filter(total_score__gt=self.total_score).count() + 1
    
    @property
    def level(self):
        """Calculate player level based on total score"""
        return min(self.total_score // 500 + 1, 100)
    
    @property
    def experience_to_next_level(self):
        """Calculate experience needed for next level"""
        current_level_exp = (self.level - 1) * 500
        next_level_exp = self.level * 500
        return next_level_exp - self.total_score
    
    def get_absolute_url(self):
        return reverse('player_profile', kwargs={'pk': self.pk})
    
    class Meta:
        ordering = ['-total_score', 'name']

class Game(TimestampedModel):
    """Enhanced Game model with advanced features"""
    # Basic Information
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    instructions = models.TextField(blank=True)
    
    # Categorization
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='games'
    )
    
    # Visual Elements
    icon = models.CharField(max_length=10, default='🎮')
    background_color = models.CharField(max_length=7, default='#667eea')
    
    # Game Settings
    max_score = models.IntegerField(default=100)
    min_score = models.IntegerField(default=0)
    difficulty_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
        default=3
    )
    estimated_duration = models.DurationField(default=timedelta(minutes=5))
    
    # Statistics
    play_count = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    average_duration = models.DurationField(default=timedelta(minutes=5))
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    release_date = models.DateField(default=timezone.now)
    
    def __str__(self):
        return self.display_name
    
    def get_absolute_url(self):
        return reverse(self.name)
    
    @property
    def popularity_score(self):
        """Calculate game popularity based on play count and average score"""
        return (self.play_count * 0.7) + (self.average_score * 0.3)
    
    def update_statistics(self):
        """Update game statistics from related scores"""
        scores = self.scores.all()
        if scores.exists():
            self.play_count = scores.count()
            self.average_score = scores.aggregate(Avg('score'))['score__avg'] or 0
            # Update average duration if available
            durations = scores.exclude(duration__isnull=True)
            if durations.exists():
                avg_duration = durations.aggregate(Avg('duration'))['duration__avg']
                self.average_duration = avg_duration
            self.save()
    
    class Meta:
        ordering = ['-is_featured', '-popularity_score', 'name']

class Achievement(TimestampedModel):
    """Player achievements system"""
    ACHIEVEMENT_TYPES = [
        ('score', 'High Score'),
        ('streak', 'Win Streak'),
        ('games', 'Games Played'),
        ('time', 'Time Based'),
        ('special', 'Special'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=10, default='🏆')
    type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    
    # Requirements
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)
    required_value = models.IntegerField(default=1)
    
    # Rewards
    points_reward = models.IntegerField(default=50)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['type', 'required_value']

class GameScore(TimestampedModel):
    """Enhanced GameScore model with detailed tracking"""
    # Basic Information
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='scores')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='scores')
    
    # Score Details
    score = models.IntegerField()
    max_possible_score = models.IntegerField(default=100)
    attempts = models.IntegerField(default=1)
    
    # Time Tracking
    duration = models.DurationField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Game Session Data
    session_id = models.UUIDField(default=uuid.uuid4, editable=False)
    game_data = models.JSONField(default=dict, blank=True)  # Store game-specific data
    
    # Difficulty and Settings
    difficulty_played = models.IntegerField(default=3)
    settings = models.JSONField(default=dict, blank=True)
    
    # Performance Metrics
    accuracy = models.FloatField(null=True, blank=True)  # For applicable games
    reaction_time = models.FloatField(null=True, blank=True)  # Average reaction time
    
    # Status
    is_completed = models.BooleanField(default=True)
    is_personal_best = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.player.name} - {self.game.display_name}: {self.score}"
    
    @property
    def score_percentage(self):
        """Calculate score as percentage of maximum"""
        return (self.score / self.max_possible_score) * 100 if self.max_possible_score > 0 else 0
    
    @property
    def performance_rating(self):
        """Get performance rating based on percentage"""
        percentage = self.score_percentage
        if percentage >= 90:
            return 'Excellent'
        elif percentage >= 75:
            return 'Good'
        elif percentage >= 60:
            return 'Average'
        elif percentage >= 40:
            return 'Below Average'
        else:
            return 'Poor'
    
    def save(self, *args, **kwargs):
        # Check if this is a personal best
        existing_best = GameScore.objects.filter(
            player=self.player,
            game=self.game,
            score__gt=self.score
        ).exists()
        
        if not existing_best:
            # Mark previous personal bests as False
            GameScore.objects.filter(
                player=self.player,
                game=self.game,
                is_personal_best=True
            ).update(is_personal_best=False)
            
            self.is_personal_best = True
        
        super().save(*args, **kwargs)
        
        # Update player statistics
        self.update_player_stats()
        
        # Update game statistics
        self.game.update_statistics()
    
    def update_player_stats(self):
        """Update related player statistics"""
        player = self.player
        player.total_games = player.scores.count()
        player.total_score = player.scores.aggregate(Sum('score'))['score__sum'] or 0
        player.highest_score = player.scores.aggregate(Max('score'))['score__max'] or 0
        player.last_played = timezone.now()
        
        # Update total playtime
        durations = player.scores.exclude(duration__isnull=True)
        if durations.exists():
            total_duration = durations.aggregate(Sum('duration'))['duration__sum']
            player.total_playtime = total_duration or timedelta(0)
        
        player.save()
    
    class Meta:
        ordering = ['-score', '-created_at']
        indexes = [
            models.Index(fields=['player', 'game']),
            models.Index(fields=['score']),
            models.Index(fields=['created_at']),
        ]

class PlayerAchievement(TimestampedModel):
    """Track player achievements"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    progress = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.player.name} - {self.achievement.name}"
    
    def check_completion(self):
        """Check if achievement is completed"""
        if self.progress >= self.achievement.required_value and not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            
            # Award points to player
            self.player.total_score += self.achievement.points_reward
            self.player.save()
            
            self.save()
            return True
        return False
    
    class Meta:
        unique_together = ['player', 'achievement']

class GameSession(TimestampedModel):
    """Track individual game sessions"""
    SESSION_STATUS = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
        ('paused', 'Paused'),
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='sessions')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='sessions')
    
    # Session Details
    session_id = models.UUIDField(default=uuid.uuid4, unique=True)
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='active')
    
    # Time Tracking
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    # Session Data
    current_data = models.JSONField(default=dict)
    moves_count = models.IntegerField(default=0)
    current_score = models.IntegerField(default=0)
    
    # Settings
    difficulty = models.IntegerField(default=3)
    settings = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.player.name} - {self.game.display_name} ({self.status})"
    
    @property
    def duration(self):
        """Calculate session duration"""
        if self.ended_at:
            return self.ended_at - self.started_at
        return timezone.now() - self.started_at
    
    def end_session(self, final_score=None):
        """End the game session"""
        self.status = 'completed'
        self.ended_at = timezone.now()
        if final_score is not None:
            self.current_score = final_score
        self.save()
    
    class Meta:
        ordering = ['-started_at']

class Leaderboard(TimestampedModel):
    """Dynamic leaderboard entries"""
    LEADERBOARD_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('all_time', 'All Time'),
    ]
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='leaderboards')
    period_type = models.CharField(max_length=20, choices=LEADERBOARD_TYPES)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Leaderboard data (JSON field with rankings)
    rankings = models.JSONField(default=list)
    
    def __str__(self):
        return f"{self.game.display_name} - {self.period_type} ({self.period_start.date()})"
    
    def update_rankings(self):
        """Update leaderboard rankings for the period"""
        scores = GameScore.objects.filter(
            game=self.game,
            created_at__gte=self.period_start,
            created_at__lte=self.period_end,
            is_completed=True
        ).select_related('player').order_by('-score')
        
        rankings = []
        for rank, score in enumerate(scores[:100], 1):  # Top 100
            rankings.append({
                'rank': rank,
                'player_id': score.player.id,
                'player_name': score.player.name,
                'score': score.score,
                'created_at': score.created_at.isoformat(),
            })
        
        self.rankings = rankings
        self.save()
    
    class Meta:
        unique_together = ['game', 'period_type', 'period_start']
        ordering = ['-period_start']
