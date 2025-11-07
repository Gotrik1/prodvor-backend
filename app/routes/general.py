
from flask import request, jsonify, Blueprint
from app import db
from app.models import Sport, Playground, Tournament, Post, Sponsor, User
from flask_jwt_extended import jwt_required, get_jwt_identity

general_bp = Blueprint('general', __name__)

# --- Sports ---
@general_bp.route('/sports', methods=['GET'])
def get_sports():
    sports = Sport.query.all()
    return jsonify([sport.to_dict() for sport in sports])

# --- Playgrounds ---
@general_bp.route('/playgrounds', methods=['GET'])
def get_playgrounds():
    playgrounds = Playground.query.all()
    return jsonify([p.to_dict() for p in playgrounds])

@general_bp.route('/playgrounds', methods=['POST'])
# @jwt_required() # Раскомментируйте, если создание площадок требует аутентификации
def create_playground():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('address'):
        return jsonify({"error": "Missing required fields: name, address"}), 400
    
    new_playground = Playground(
        name=data['name'], 
        address=data['address'],
        type=data.get('type'),
        surface=data.get('surface')
    )
    db.session.add(new_playground)
    db.session.commit()
    return jsonify(new_playground.to_dict()), 201

# --- Tournaments ---
@general_bp.route('/tournaments', methods=['GET'])
def get_tournaments():
    tournaments = Tournament.query.all()
    return jsonify([t.to_dict() for t in tournaments])

@general_bp.route('/tournaments/<int:tournament_id>', methods=['GET'])
def get_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    return jsonify(tournament.to_dict())

@general_bp.route('/tournaments', methods=['POST'])
# @jwt_required() # Раскомментируйте, если создание турниров требует аутентификации
def create_tournament():
    data = request.get_json()
    # Добавьте валидацию полей, как в create_playground
    new_tournament = Tournament(**data) # Быстрое создание, если ключи JSON совпадают с полями модели
    db.session.add(new_tournament)
    db.session.commit()
    return jsonify(new_tournament.to_dict()), 201

# --- Posts ---
@general_bp.route('/posts', methods=['GET'])
def get_posts():
    # ?team_id=X или ?user_id=Y для фильтрации
    team_id = request.args.get('team_id', type=int)
    user_id = request.args.get('user_id', type=int)
    
    query = Post.query
    if team_id:
        query = query.filter_by(teamId=team_id)
    if user_id:
        query = query.filter_by(authorId=user_id)
        
    posts = query.order_by(Post.timestamp.desc()).all()
    return jsonify([post.to_dict() for post in posts])

@general_bp.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or not data.get('content'):
        return jsonify({"error": "Content is required"}), 400

    new_post = Post(
        authorId=user_id,
        content=data['content'],
        teamId=data.get('teamId') # Пост может быть от имени команды
    )
    db.session.add(new_post)
    db.session.commit()
    return jsonify(new_post.to_dict()), 201

# --- Sponsors ---
@general_bp.route('/sponsors', methods=['GET'])
def get_sponsors():
    sponsors = Sponsor.query.all()
    return jsonify([s.to_dict() for s in sponsors])
