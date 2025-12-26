# Shut the Box

A Progressive Web App (PWA) implementation of the classic dice game "Shut the Box" built with Python and Flask.

## About the Game

Shut the Box is a classic dice game where players roll a pair of dice and flip down corresponding numbered tiles on a board. The goal is to "shut the box" by closing all tiles, or to have the lowest score by summing the remaining numbers when no more moves can be made.

### Game Rules

1. Players roll a pair of dice each round
2. All players play with the same rolled number per round
3. Each player must flip down one or more tiles that sum to the dice total
4. If a player cannot make a valid move, they are out and their score is the sum of remaining tiles
5. The game ends when one player shuts the box (closes all tiles) or no players can make a move
6. The player with the lowest score wins

### Features

- Support for 1-12 players per game
- Configurable tile count (1-10 or 1-12)
- Real-time multiplayer gameplay
- PWA support for mobile installation on Android and iOS
- Simple username/password authentication

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/thiagoralves/shut-the-box.git
   cd shut-the-box
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and set your SECRET_KEY
   ```

5. Run the application:
   ```bash
   python run.py
   ```

6. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
shut-the-box/
├── app/
│   ├── __init__.py      # Flask app factory
│   ├── auth.py          # Authentication routes
│   ├── models.py        # Database models
│   └── routes.py        # Main routes
├── static/
│   ├── css/
│   │   └── style.css    # Application styles
│   ├── icons/           # PWA icons
│   ├── js/
│   │   └── sw.js        # Service worker
│   └── manifest.json    # PWA manifest
├── templates/
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   ├── login.html       # Login page
│   └── signup.html      # Sign up page
├── .env.example         # Environment variables template
├── requirements.txt     # Python dependencies
├── run.py              # Application entry point
└── README.md           # This file
```

## PWA Installation

### Android
1. Open the app in Chrome
2. Tap the menu (three dots) and select "Add to Home screen"
3. Follow the prompts to install

### iOS
1. Open the app in Safari
2. Tap the Share button
3. Select "Add to Home Screen"
4. Tap "Add" to confirm

## Development

### Running in Development Mode

```bash
python run.py
```

The app will run with debug mode enabled and auto-reload on code changes.

### Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

Make sure to:
- Set a strong `SECRET_KEY` in your environment
- Use a production database (PostgreSQL recommended)
- Configure HTTPS

## License

This project is for personal use among family and friends.

## Contributing

This is a personal project, but suggestions and feedback are welcome!
