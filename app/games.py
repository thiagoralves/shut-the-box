from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Game, GamePlayer

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
    players = GamePlayer.query.filter_by(game_id=game_id).all()
    current_player = GamePlayer.query.filter_by(game_id=game_id, user_id=current_user.id).first()
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
