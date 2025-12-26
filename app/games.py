from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Game, GamePlayer
import random

games_bp = Blueprint('games', __name__)


@games_bp.route('/games')
@login_required
def list_games():
    available_games = Game.query.filter_by(status='waiting').order_by(Game.created_at.desc()).all()
    my_games = Game.query.join(GamePlayer).filter(
        GamePlayer.user_id == current_user.id,
        Game.status.in_(['waiting', 'playing'])
    ).order_by(Game.created_at.desc()).all()
    return render_template('games/list.html', available_games=available_games, my_games=my_games)


@games_bp.route('/games/create', methods=['GET', 'POST'])
@login_required
def create_game():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        max_tiles = request.form.get('max_tiles', '10')
        max_players = request.form.get('max_players', '12')
        
        if not name:
            flash('Please enter a game name.', 'error')
            return render_template('games/create.html')
        
        if len(name) < 3:
            flash('Game name must be at least 3 characters long.', 'error')
            return render_template('games/create.html')
        
        try:
            max_tiles = int(max_tiles)
            max_players = int(max_players)
        except ValueError:
            flash('Invalid settings.', 'error')
            return render_template('games/create.html')
        
        if max_tiles not in [10, 12]:
            flash('Max tiles must be 10 or 12.', 'error')
            return render_template('games/create.html')
        
        if max_players < 1 or max_players > 12:
            flash('Max players must be between 1 and 12.', 'error')
            return render_template('games/create.html')
        
        game = Game(
            name=name,
            max_tiles=max_tiles,
            max_players=max_players,
            created_by=current_user.id,
            status='waiting'
        )
        db.session.add(game)
        db.session.commit()
        
        tiles = ','.join(str(i) for i in range(1, max_tiles + 1))
        player = GamePlayer(
            game_id=game.id,
            user_id=current_user.id,
            tiles_remaining=tiles
        )
        db.session.add(player)
        db.session.commit()
        
        flash(f'Game "{name}" created successfully!', 'success')
        return redirect(url_for('games.view_game', game_id=game.id))
    
    return render_template('games/create.html')


@games_bp.route('/games/<int:game_id>')
@login_required
def view_game(game_id):
    game = Game.query.get_or_404(game_id)
    current_player = GamePlayer.query.filter_by(game_id=game_id, user_id=current_user.id).first()
    
    if game.status == 'playing' and current_player:
        return redirect(url_for('games.play_game', game_id=game_id))
    
    if game.status == 'finished':
        return redirect(url_for('games.game_results', game_id=game_id))
    
    players = GamePlayer.query.filter_by(game_id=game_id).all()
    is_creator = game.created_by == current_user.id
    return render_template('games/view.html', game=game, players=players, 
                          current_player=current_player, is_creator=is_creator)


@games_bp.route('/games/<int:game_id>/join', methods=['POST'])
@login_required
def join_game(game_id):
    game = Game.query.get_or_404(game_id)
    
    if game.status != 'waiting':
        flash('This game has already started.', 'error')
        return redirect(url_for('games.list_games'))
    
    existing_player = GamePlayer.query.filter_by(game_id=game_id, user_id=current_user.id).first()
    if existing_player:
        flash('You have already joined this game.', 'info')
        return redirect(url_for('games.view_game', game_id=game_id))
    
    player_count = GamePlayer.query.filter_by(game_id=game_id).count()
    if player_count >= game.max_players:
        flash('This game is full.', 'error')
        return redirect(url_for('games.list_games'))
    
    tiles = ','.join(str(i) for i in range(1, game.max_tiles + 1))
    player = GamePlayer(
        game_id=game_id,
        user_id=current_user.id,
        tiles_remaining=tiles
    )
    db.session.add(player)
    db.session.commit()
    
    flash(f'You have joined "{game.name}"!', 'success')
    return redirect(url_for('games.view_game', game_id=game_id))


@games_bp.route('/games/<int:game_id>/leave', methods=['POST'])
@login_required
def leave_game(game_id):
    game = Game.query.get_or_404(game_id)
    
    if game.status != 'waiting':
        flash('Cannot leave a game that has already started.', 'error')
        return redirect(url_for('games.view_game', game_id=game_id))
    
    player = GamePlayer.query.filter_by(game_id=game_id, user_id=current_user.id).first()
    if not player:
        flash('You are not in this game.', 'error')
        return redirect(url_for('games.list_games'))
    
    if game.created_by == current_user.id:
        GamePlayer.query.filter_by(game_id=game_id).delete()
        db.session.delete(game)
        db.session.commit()
        flash('Game has been deleted.', 'info')
        return redirect(url_for('games.list_games'))
    
    db.session.delete(player)
    db.session.commit()
    flash('You have left the game.', 'info')
    return redirect(url_for('games.list_games'))


@games_bp.route('/games/<int:game_id>/start', methods=['POST'])
@login_required
def start_game(game_id):
    game = Game.query.get_or_404(game_id)
    
    if game.created_by != current_user.id:
        flash('Only the host can start the game.', 'error')
        return redirect(url_for('games.view_game', game_id=game_id))
    
    if game.status != 'waiting':
        flash('Game has already started.', 'error')
        return redirect(url_for('games.view_game', game_id=game_id))
    
    player_count = GamePlayer.query.filter_by(game_id=game_id).count()
    if player_count < 1:
        flash('Need at least 1 player to start.', 'error')
        return redirect(url_for('games.view_game', game_id=game_id))
    
    game.status = 'playing'
    game.current_round = 1
    game.round_phase = 'rolling'
    
    for player in game.players:
        tiles = ','.join(str(i) for i in range(1, game.max_tiles + 1))
        player.tiles_remaining = tiles
        player.is_out = False
        player.has_submitted = False
        player.round_score = 0
    
    db.session.commit()
    flash('Game started! Roll the dice to begin.', 'success')
    return redirect(url_for('games.play_game', game_id=game_id))


@games_bp.route('/games/<int:game_id>/play')
@login_required
def play_game(game_id):
    game = Game.query.get_or_404(game_id)
    current_player = GamePlayer.query.filter_by(game_id=game_id, user_id=current_user.id).first()
    
    if not current_player:
        flash('You are not in this game.', 'error')
        return redirect(url_for('games.list_games'))
    
    if game.status == 'waiting':
        return redirect(url_for('games.view_game', game_id=game_id))
    
    if game.status == 'finished':
        return redirect(url_for('games.game_results', game_id=game_id))
    
    players = GamePlayer.query.filter_by(game_id=game_id).all()
    is_creator = game.created_by == current_user.id
    
    can_flip = (game.round_phase == 'flipping' and 
                not current_player.is_out and 
                not current_player.has_submitted and
                current_player.can_make_move(game.get_dice_total()))
    
    must_pass = (game.round_phase == 'flipping' and 
                 not current_player.is_out and 
                 not current_player.has_submitted and
                 not current_player.can_make_move(game.get_dice_total()))
    
    return render_template('games/play.html', game=game, players=players,
                          current_player=current_player, is_creator=is_creator,
                          can_flip=can_flip, must_pass=must_pass)


@games_bp.route('/games/<int:game_id>/roll', methods=['POST'])
@login_required
def roll_dice(game_id):
    game = Game.query.get_or_404(game_id)
    
    if game.status != 'playing':
        flash('Game is not in progress.', 'error')
        return redirect(url_for('games.view_game', game_id=game_id))
    
    if game.round_phase != 'rolling':
        flash('Not time to roll dice.', 'error')
        return redirect(url_for('games.play_game', game_id=game_id))
    
    if game.created_by != current_user.id:
        flash('Only the host can roll the dice.', 'error')
        return redirect(url_for('games.play_game', game_id=game_id))
    
    game.dice1 = random.randint(1, 6)
    game.dice2 = random.randint(1, 6)
    game.round_phase = 'flipping'
    
    for player in game.players:
        player.has_submitted = False
    
    db.session.commit()
    flash(f'Rolled {game.dice1} + {game.dice2} = {game.get_dice_total()}!', 'info')
    return redirect(url_for('games.play_game', game_id=game_id))


@games_bp.route('/games/<int:game_id>/flip', methods=['POST'])
@login_required
def flip_tiles(game_id):
    game = Game.query.get_or_404(game_id)
    current_player = GamePlayer.query.filter_by(game_id=game_id, user_id=current_user.id).first()
    
    if not current_player:
        flash('You are not in this game.', 'error')
        return redirect(url_for('games.list_games'))
    
    if game.status != 'playing' or game.round_phase != 'flipping':
        flash('Cannot flip tiles now.', 'error')
        return redirect(url_for('games.play_game', game_id=game_id))
    
    if current_player.is_out or current_player.has_submitted:
        flash('You have already submitted this turn.', 'error')
        return redirect(url_for('games.play_game', game_id=game_id))
    
    tiles_str = request.form.get('tiles', '')
    if not tiles_str:
        flash('Please select tiles to flip.', 'error')
        return redirect(url_for('games.play_game', game_id=game_id))
    
    try:
        tiles_to_flip = [int(t) for t in tiles_str.split(',')]
    except ValueError:
        flash('Invalid tile selection.', 'error')
        return redirect(url_for('games.play_game', game_id=game_id))
    
    dice_total = game.get_dice_total()
    
    if not current_player.is_valid_flip(tiles_to_flip, dice_total):
        flash(f'Invalid flip. Tiles must sum to {dice_total} and be available.', 'error')
        return redirect(url_for('games.play_game', game_id=game_id))
    
    current_tiles = current_player.get_tiles_list()
    new_tiles = [t for t in current_tiles if t not in tiles_to_flip]
    current_player.set_tiles_list(new_tiles)
    current_player.has_submitted = True
    
    if not new_tiles:
        current_player.round_score = 0
        flash('You shut the box! 0 points this round!', 'success')
    
    db.session.commit()
    
    check_turn_end(game)
    
    return redirect(url_for('games.play_game', game_id=game_id))


@games_bp.route('/games/<int:game_id>/pass', methods=['POST'])
@login_required
def pass_turn(game_id):
    game = Game.query.get_or_404(game_id)
    current_player = GamePlayer.query.filter_by(game_id=game_id, user_id=current_user.id).first()
    
    if not current_player:
        flash('You are not in this game.', 'error')
        return redirect(url_for('games.list_games'))
    
    if game.status != 'playing' or game.round_phase != 'flipping':
        flash('Cannot pass now.', 'error')
        return redirect(url_for('games.play_game', game_id=game_id))
    
    if current_player.is_out or current_player.has_submitted:
        flash('You have already submitted this turn.', 'error')
        return redirect(url_for('games.play_game', game_id=game_id))
    
    current_player.is_out = True
    current_player.has_submitted = True
    current_player.round_score = current_player.get_tiles_sum()
    
    db.session.commit()
    flash(f'You are out this round with {current_player.round_score} points.', 'info')
    
    check_turn_end(game)
    
    return redirect(url_for('games.play_game', game_id=game_id))


def check_turn_end(game):
    players = GamePlayer.query.filter_by(game_id=game.game_id if hasattr(game, 'game_id') else game.id).all()
    
    all_submitted = all(p.has_submitted for p in players)
    all_out = all(p.is_out for p in players)
    any_shut_box = any(not p.get_tiles_list() for p in players)
    
    if all_out or any_shut_box:
        end_round(game)
    elif all_submitted:
        game.round_phase = 'rolling'
        for player in players:
            player.has_submitted = False
        db.session.commit()


def end_round(game):
    players = GamePlayer.query.filter_by(game_id=game.id).all()
    
    for player in players:
        if not player.is_out and player.get_tiles_list():
            player.round_score = player.get_tiles_sum()
        player.score += player.round_score
    
    db.session.commit()
    
    max_score = max(p.score for p in players)
    if max_score >= 100:
        end_game(game)
    else:
        game.round_phase = 'round_end'
        db.session.commit()


def end_game(game):
    players = GamePlayer.query.filter_by(game_id=game.id).all()
    
    min_score = min(p.score for p in players)
    winner = next(p for p in players if p.score == min_score)
    
    game.status = 'finished'
    game.winner_id = winner.user_id
    game.round_phase = 'finished'
    db.session.commit()


@games_bp.route('/games/<int:game_id>/next-round', methods=['POST'])
@login_required
def next_round(game_id):
    game = Game.query.get_or_404(game_id)
    
    if game.created_by != current_user.id:
        flash('Only the host can start the next round.', 'error')
        return redirect(url_for('games.play_game', game_id=game_id))
    
    if game.round_phase != 'round_end':
        flash('Cannot start next round now.', 'error')
        return redirect(url_for('games.play_game', game_id=game_id))
    
    game.current_round += 1
    game.round_phase = 'rolling'
    game.dice1 = 0
    game.dice2 = 0
    
    for player in game.players:
        tiles = ','.join(str(i) for i in range(1, game.max_tiles + 1))
        player.tiles_remaining = tiles
        player.is_out = False
        player.has_submitted = False
        player.round_score = 0
    
    db.session.commit()
    flash(f'Round {game.current_round} started!', 'success')
    return redirect(url_for('games.play_game', game_id=game_id))


@games_bp.route('/games/<int:game_id>/results')
@login_required
def game_results(game_id):
    game = Game.query.get_or_404(game_id)
    players = GamePlayer.query.filter_by(game_id=game_id).order_by(GamePlayer.score.asc()).all()
    current_player = GamePlayer.query.filter_by(game_id=game_id, user_id=current_user.id).first()
    
    return render_template('games/results.html', game=game, players=players,
                          current_player=current_player)
