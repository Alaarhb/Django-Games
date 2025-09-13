from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from django.db.models import (
    Count, Avg, Sum, Max, Min, Q, F, Case, When, Value, 
    IntegerField, Prefetch, Subquery, OuterRef
)
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db import transaction
import random
import json
from datetime import timedelta
from .models import (
    Player, Game, GameScore, Category, Achievement, 
    PlayerAchievement, GameSession, Leaderboard
)
from .database_operations import DatabaseOperations


def home_with_advanced_queries(request):
    """Enhanced home view using custom QuerySet methods"""
    
    # Using custom QuerySet methods
    context = {
        # Featured games with comprehensive statistics
        'featured_games': Game.objects.featured().with_statistics().select_related('category')[:6],
        
        # Top players using custom method
        'top_players': Player.objects.top_players(10).with_statistics(),
        
        # Trending games using custom method
        'trending_games': Game.objects.trending(days=7)[:5],
        
        # Recent high scores with performance rating
        'recent_scores': GameScore.objects.recent(days=7).with_performance_rating()
                         .select_related('player', 'game')[:15],
        
        # Categories with game counts
        'categories': Category.objects.active().prefetch_related('games')
                     .annotate(game_count=models.Count('games')),
        
        # Advanced statistics using QuerySet methods
        'stats': {
            'total_active_players': Player.objects.active().count(),
            'games_today': GameScore.objects.created_today().count(),
            'perfect_scores_week': GameScore.objects.created_this_week().perfect_scores().count(),
            'new_players_week': Player.objects.created_this_week().count(),
        },
        
        # Leaderboard preview using custom method
        'weekly_leaderboard': GameScore.objects.leaderboard(period='week', limit=5),
    }
    
    return render(request, 'games/home_advanced.html', context)

def player_dashboard(request, pk):
    """Advanced player dashboard using custom QuerySet methods"""
    player = get_object_or_404(Player, pk=pk, is_active=True)
    
    # Using custom QuerySet methods for comprehensive data
    context = {
        'player': player,
        
        # Player's recent activity
        'recent_scores': player.scores.recent(days=30).with_performance_rating()
                        .select_related('game')[:20],
        
        # Personal bests across all games
        'personal_bests': player.scores.personal_bests().select_related('game'),
        
        # High scores (above 80%)
        'high_scores': player.scores.high_scores(80).select_related('game')[:10],
        
        # Quick games completed
        'quick_completions': player.scores.quick_games(5).select_related('game')[:5],
        
        # Game statistics
        'game_performance': player.scores.values('game__display_name', 'game__icon')
                           .annotate(
                               games_played=models.Count('id'),
                               best_score=models.Max('score'),
                               avg_score=models.Avg('score'),
                               last_played=models.Max('created_at')
                           ).order_by('-games_played'),
        
        # Achievements
        'completed_achievements': player.achievements.filter(is_completed=True)
                                 .select_related('achievement'),
        'progress_achievements': player.achievements.filter(is_completed=False)
                                .select_related('achievement'),
        
        # Performance trends
        'performance_stats': player.scores.statistics_for_period(),
    }
    
    return render(request, 'games/player_dashboard.html', context)

class GameListView(ListView):
    """Advanced game list view using custom QuerySets"""
    model = Game
    template_name = 'games/game_list.html'
    context_object_name = 'games'
    paginate_by = 12
    
    def get_queryset(self):
        """Build queryset using custom methods"""
        queryset = Game.objects.active().with_statistics().select_related('category')
        
        # Filter parameters
        category = self.request.GET.get('category')
        difficulty = self.request.GET.get('difficulty')
        search = self.request.GET.get('search')
        sort = self.request.GET.get('sort', 'popular')
        
        # Apply filters using custom QuerySet methods
        if category:
            queryset = queryset.by_category(category)
        
        if difficulty:
            if difficulty == 'easy':
                queryset = queryset.easy_games()
            elif difficulty == 'medium':
                queryset = queryset.medium_games()
            elif difficulty == 'hard':
                queryset = queryset.hard_games()
        
        if search:
            queryset = queryset.search(search)
        
        # Apply sorting
        if sort == 'popular':
            queryset = queryset.order_by('-total_plays', '-avg_score')
        elif sort == 'rating':
            queryset = queryset.highly_rated().order_by('-avg_score')
        elif sort == 'new':
            queryset = queryset.order_by('-release_date')
        elif sort == 'trending':
            queryset = queryset.trending()
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter context
        context.update({
            'categories': Category.objects.active(),
            'current_category': self.request.GET.get('category'),
            'current_difficulty': self.request.GET.get('difficulty'),
            'current_search': self.request.GET.get('search', ''),
            'current_sort': self.request.GET.get('sort', 'popular'),
            
            # Additional stats using QuerySet methods
            'featured_games': Game.objects.featured()[:3],
            'new_releases': Game.objects.new_releases()[:3],
        })
        
        return context

class LeaderboardView(ListView):
    """Advanced leaderboard using custom QuerySet methods"""
    model = GameScore
    template_name = 'games/leaderboard_advanced.html'
    context_object_name = 'scores'
    paginate_by = 25
    
    def get_queryset(self):
        """Build leaderboard using custom QuerySet methods"""
        game_id = self.request.GET.get('game')
        period = self.request.GET.get('period', 'all_time')
        
        game = None
        if game_id:
            try:
                game = Game.objects.get(id=game_id)
            except Game.DoesNotExist:
                pass
        
        # Use custom QuerySet method for leaderboard
        queryset = GameScore.objects.leaderboard(game=game, period=period, limit=1000)
        
        return queryset.with_performance_rating()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        game_id = self.request.GET.get('game')
        period = self.request.GET.get('period', 'all_time')
        
        context.update({
            'games': Game.objects.active().order_by('display_name'),
            'current_game': game_id,
            'current_period': period,
            
            # Statistics using QuerySet methods
            'period_stats': GameScore.objects.statistics_for_period(),
            'perfect_scores': GameScore.objects.perfect_scores().count(),
            'total_players': Player.objects.with_scores().count(),
        })
        
        return context

def analytics_dashboard_advanced(request):
    """Advanced analytics using custom QuerySet methods"""
    if not request.user.is_staff:
        raise Http404("Access denied")
    
    days = int(request.GET.get('days', 30))
    
    context = {
        # Player analytics using custom methods
        'player_stats': {
            'total_players': Player.objects.active().count(),
            'new_players': Player.objects.recent(days).count(),
            'active_players': Player.objects.active_recently(days).count(),
            'inactive_players': Player.objects.inactive_players(days).count(),
            'expert_players': Player.objects.experts().count(),
            'beginners': Player.objects.beginners().count(),
        },
        
        # Game analytics using custom methods
        'game_stats': {
            'total_games': Game.objects.active().count(),
            'featured_games': Game.objects.featured().count(),
            'popular_games': Game.objects.popular().count(),
            'new_releases': Game.objects.new_releases().count(),
        },
        
        # Score analytics using custom methods
        'score_stats': GameScore.objects.recent(days).statistics_for_period(),
        
        # Top performing content
        'top_games': Game.objects.with_statistics().order_by('-total_plays')[:10],
        'top_players': Player.objects.with_statistics().order_by('-total_score')[:10],
        'recent_perfect_scores': GameScore.objects.recent(days).perfect_scores()
                                .select_related('player', 'game')[:10],
        
        # Trending analysis
        'trending_games': Game.objects.trending(days),
        'period_days': days,
    }
    
    return render(request, 'games/analytics_advanced.html', context)
