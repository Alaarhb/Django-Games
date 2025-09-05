# Django Games Project

A collection of three interactive web games built with Django:

## Games Included

1. **🔢 Number Guessing Game**
   - Guess a secret number between 1-100
   - Score based on number of attempts
   - Hints provided (too high/too low)

2. **❌ Tic Tac Toe**
   - Classic 3x3 grid game
   - Play against computer AI
   - Win detection and scoring

3. **✂️ Rock Paper Scissors**
   - Battle against the computer
   - Win/loss statistics tracking
   - Score accumulation system

## Features

- **Score Tracking**: All games save high scores to database
- **Player Statistics**: Track wins, attempts, and performance
- **Responsive Design**: Modern, mobile-friendly interface
- **Admin Panel**: Manage scores and players through Django admin
- **Session Management**: Maintains game state across requests


## File Structure

```
games_project/
├── manage.py
├── requirements.txt
├── README.md
├── games_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── games/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── models.py
    ├── tests.py
    ├── urls.py
    ├── views.py
    ├── management/
    │   └── commands/
    │       ├── reset_scores.py
    │       └── generate_test_data.py
    ├── templatetags/
    │   └── games_extras.py
    └── templates/
        └── games/
            ├── base.html
            ├── home.html
            ├── number_guess.html
            ├── tic_tac_toe.html
            └── rock_paper_scissors.html
```

## Technologies Used

- **Backend**: Django 4.2+
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite (default)
- **Styling**: Custom CSS with gradients and animations
- **AJAX**: For real-time Tic Tac Toe gameplay

## Game Logic

### Number Guessing
- Random number generation (1-100)
- Session-based game state
- Score calculation: max(100 - attempts, 10)

### Tic Tac Toe
- AJAX-based real-time gameplay
- Simple AI opponent
- Win detection algorithm

### Rock Paper Scissors
- Random computer choice
- Win/loss/tie determination
- Session-based statistics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is open source and available under the MIT License.
"""
