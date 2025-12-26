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
    round_phase = db.Column(db.String(20), default='waiting')
    winner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    creator = db.relationship('User', backref='created_games', foreign_keys=[created_by])
    winner = db.relationship('User', backref='won_games', foreign_keys=[winner_id])
    players = db.relationship('GamePlayer', backref='game', lazy='dynamic')
    
    def get_dice_total(self):
        return self.dice1 + self.dice2
    
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
    has_submitted = db.Column(db.Boolean, default=False)
    round_score = db.Column(db.Integer, default=0)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='game_participations')
    
    def get_tiles_list(self):
        if not self.tiles_remaining:
            return []
        return [int(t) for t in self.tiles_remaining.split(',') if t]
    
    def set_tiles_list(self, tiles):
        self.tiles_remaining = ','.join(str(t) for t in sorted(tiles))
    
    def get_tiles_sum(self):
        return sum(self.get_tiles_list())
    
    def can_make_move(self, dice_total):
        tiles = self.get_tiles_list()
        if not tiles:
            return False
        return self._can_sum_to(tiles, dice_total)
    
    def _can_sum_to(self, tiles, target):
        if target == 0:
            return True
        if target < 0 or not tiles:
            return False
        for i, tile in enumerate(tiles):
            if tile <= target:
                remaining = tiles[:i] + tiles[i+1:]
                if self._can_sum_to(remaining, target - tile):
                    return True
        return False
    
    def is_valid_flip(self, tiles_to_flip, dice_total):
        current_tiles = self.get_tiles_list()
        for tile in tiles_to_flip:
            if tile not in current_tiles:
                return False
        return sum(tiles_to_flip) == dice_total
    
    def __repr__(self):
        return f'<GamePlayer {self.user_id} in Game {self.game_id}>'
