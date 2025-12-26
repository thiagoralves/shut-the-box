from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Game(db.Model):
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    max_tiles = db.Column(db.Integer, default=10)
    max_players = db.Column(db.Integer, default=12)
    status = db.Column(db.String(20), default='waiting')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    current_round = db.Column(db.Integer, default=0)
    dice1 = db.Column(db.Integer, default=0)
    dice2 = db.Column(db.Integer, default=0)
    
    creator = db.relationship('User', backref='created_games')
    players = db.relationship('GamePlayer', backref='game', lazy='dynamic')
    
    def __repr__(self):
        return f'<Game {self.name}>'


class GamePlayer(db.Model):
    __tablename__ = 'game_players'
    
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tiles_remaining = db.Column(db.String(50), nullable=True)
    score = db.Column(db.Integer, default=0)
    is_out = db.Column(db.Boolean, default=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='game_participations')
    
    def __repr__(self):
        return f'<GamePlayer {self.user_id} in Game {self.game_id}>'
