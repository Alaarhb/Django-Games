from django.urls import path
from ..games import views

urlpatterns = [
    path('', views.home, name='home'),
    path('number-guess/', views.number_guess, name='number_guess'),
    path('tic-tac-toe/', views.tic_tac_toe, name='tic_tac_toe'),
    path('tic-tac-toe/move/', views.tic_tac_toe_move, name='tic_tac_toe_move'),
    path('rock-paper-scissors/', views.rock_paper_scissors, name='rock_paper_scissors'),
    path('reset-rps/', views.reset_rps_stats, name='reset_rps_stats'),
]