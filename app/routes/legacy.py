from flask import Blueprint, jsonify, request
from app import db
from app.models import Team, Tournament, Post, Comment, Playground, Quest, Achievement, Sponsor, PlayerProfile, RefereeProfile, CoachProfile, User, TeamMembers
from sqlalchemy.orm import joinedload

legacy_bp = Blueprint('legacy', __name__)

@legacy_bp.route('/')
def index():
    """
    Legacy Index
    ---
    tags:
        - Legacy
    responses:
        200:
            description: Welcome message
    """
    return jsonify({'message': 'Welcome to the API!'})

@legacy_bp.route('/tournaments', methods=['GET'])
def get_tournaments():
    """
    Get all tournaments
    ---
    tags:
        - Legacy - Tournaments
    responses:
        200:
            description: A list of tournaments
    """
    tournaments = Tournament.query.all()
    return jsonify([t.to_dict() for t in tournaments])

@legacy_bp.route('/tournaments/<int:tournament_id>', methods=['GET'])
def get_tournament(tournament_id):
    """
    Get a specific tournament
    ---
    tags:
        - Legacy - Tournaments
    parameters:
        -   name: tournament_id
            in: path
            required: true
            type: integer
    responses:
        200:
            description: A single tournament
        404:
            description: Tournament not found
    """
    tournament = db.get_or_404(Tournament, tournament_id)
    return jsonify(tournament.to_dict())

@legacy_bp.route('/tournaments', methods=['POST'])
def create_tournament():
    """
    Create a new tournament
    ---
    tags:
        - Legacy - Tournaments
    parameters:
        -   in: body
            name: body
            required: true
            schema:
                type: object
                required:
                    - name
                    - game
                    - status
                    - maxParticipants
                    - startDate
                properties:
                    name:
                        type: string
                    game:
                        type: string
                    status:
                        type: string
                    maxParticipants:
                        type: integer
                    startDate:
                        type: string
                        format: date-time
    responses:
        201:
            description: Tournament created successfully
        400:
            description: Missing data
    """
    data = request.get_json()
    if not data or not all(k in data for k in ('name', 'game', 'status', 'maxParticipants', 'startDate')):
        return jsonify({'error': 'Missing data'}), 400

    new_tournament = Tournament(
        name=data['name'],
        game=data['game'],
        status=data['status'],
        maxParticipants=data['maxParticipants'],
        startDate=data['startDate']
    )

    db.session.add(new_tournament)
    db.session.commit()

    return jsonify(new_tournament.to_dict()), 201

@legacy_bp.route('/posts', methods=['GET'])
def get_posts():
    """
    Get all posts
    ---
    tags:
        - Legacy - Posts
    responses:
        200:
            description: A list of posts
    """
    posts = Post.query.all()
    return jsonify([p.to_dict() for p in posts])

@legacy_bp.route('/posts', methods=['POST'])
def create_post():
    """
    Create a new post
    ---
    tags:
        - Legacy - Posts
    parameters:
        -   in: body
            name: body
            required: true
            schema:
                type: object
                required:
                    - authorId
                    - content
                properties:
                    authorId:
                        type: integer
                    content:
                        type: string
                    teamId:
                        type: integer
    responses:
        201:
            description: Post created successfully
        400:
            description: Missing data
        404:
            description: Author or Team not found
    """
    data = request.get_json()
    if not data or not all(k in data for k in ('authorId', 'content')):
        return jsonify({'error': 'Missing data'}), 400

    if not db.get_or_404(User, data['authorId']):
        return jsonify({'error': 'Author not found'}), 400

    teamId = data.get('teamId')
    if teamId and not db.get_or_404(Team, teamId):
         return jsonify({'error': 'Team not found'}), 400

    new_post = Post(
        authorId=data['authorId'],
        content=data['content'],
        teamId=teamId
    )

    db.session.add(new_post)
    db.session.commit()

    return jsonify(new_post.to_dict()), 201

@legacy_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    """
    Get all comments for a post
    ---
    tags:
        - Legacy - Posts
    parameters:
        -   name: post_id
            in: path
            required: true
            type: integer
    responses:
        200:
            description: A list of comments for a post
        404:
            description: Post not found
    """
    post = db.get_or_404(Post, post_id)
    comments = post.comments
    return jsonify([c.to_dict() for c in comments])

@legacy_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
def create_comment(post_id):
    """
    Create a new comment on a post
    ---
    tags:
        - Legacy - Posts
    parameters:
        -   name: post_id
            in: path
            required: true
            type: integer
        -   in: body
            name: body
            required: true
            schema:
                type: object
                required:
                    - authorId
                    - text
                properties:
                    authorId:
                        type: integer
                    text:
                        type: string
    responses:
        201:
            description: Comment created successfully
        400:
            description: Missing data
        404:
            description: Post or Author not found
    """
    data = request.get_json()
    if not data or not all(k in data for k in ('authorId', 'text')):
        return jsonify({'error': 'Missing data'}), 400

    if not db.get_or_404(Post, post_id):
        return jsonify({'error': 'Post not found'}), 404

    if not db.get_or_404(User, data['authorId']):
        return jsonify({'error': 'Author not found'}), 400

    new_comment = Comment(
        postId=post_id,
        authorId=data['authorId'],
        text=data['text']
    )

    db.session.add(new_comment)
    db.session.commit()

    return jsonify(new_comment.to_dict()), 201

@legacy_bp.route('/playgrounds', methods=['GET'])
def get_playgrounds():
    """
    Get all playgrounds
    ---
    tags:
        - Legacy - Playgrounds
    responses:
        200:
            description: A list of playgrounds
    """
    playgrounds = Playground.query.all()
    return jsonify([p.to_dict() for p in playgrounds])

@legacy_bp.route('/playgrounds', methods=['POST'])
def create_playground():
    """
    Create a new playground
    ---
    tags:
        - Legacy - Playgrounds
    parameters:
        -   in: body
            name: body
            required: true
            schema:
                type: object
                required:
                    - name
                    - address
                    - type
                    - surface
                properties:
                    name:
                        type: string
                    address:
                        type: string
                    type:
                        type: string
                    surface:
                        type: string
    responses:
        201:
            description: Playground created successfully
        400:
            description: Missing data
    """
    data = request.get_json()
    if not data or not all(k in data for k in ('name', 'address', 'type', 'surface')):
        return jsonify({'error': 'Missing data'}), 400

    new_playground = Playground(
        name=data['name'],
        address=data['address'],
        type=data['type'],
        surface=data['surface']
    )

    db.session.add(new_playground)
    db.session.commit()

    return jsonify(new_playground.to_dict()), 201

@legacy_bp.route('/quests', methods=['GET'])
def get_quests():
    """
    Get all quests
    ---
    tags:
        - Legacy - Quests
    responses:
        200:
            description: A list of quests
    """
    quests = Quest.query.all()
    return jsonify([q.to_dict() for q in quests])

@legacy_bp.route('/achievements', methods=['GET'])
def get_achievements():
    """
    Get all achievements
    ---
    tags:
        - Legacy - Achievements
    responses:
        200:
            description: A list of achievements
    """
    achievements = Achievement.query.all()
    return jsonify([a.to_dict() for a in achievements])

@legacy_bp.route('/sponsors', methods=['GET'])
def get_sponsors():
    """
    Get all sponsors
    ---
    tags:
        - Legacy - Sponsors
    responses:
        200:
            description: A list of sponsors
    """
    sponsors = Sponsor.query.all()
    return jsonify([s.to_dict() for s in sponsors])

@legacy_bp.route('/sponsors', methods=['POST'])
def create_sponsor():
    """
    Create a new sponsor
    ---
    tags:
        - Legacy - Sponsors
    parameters:
        -   in: body
            name: body
            required: true
            schema:
                type: object
                required:
                    - name
                    - logoUrl
                    - contribution
                properties:
                    name:
                        type: string
                    logoUrl:
                        type: string
                    contribution:
                        type: string
    responses:
        201:
            description: Sponsor created successfully
        400:
            description: Missing data
    """
    data = request.get_json()
    if not data or not all(k in data for k in ('name', 'logoUrl', 'contribution')):
        return jsonify({'error': 'Missing data'}), 400

    new_sponsor = Sponsor(
        name=data['name'],
        logoUrl=data['logoUrl'],
        contribution=data['contribution']
    )

    db.session.add(new_sponsor)
    db.session.commit()

    return jsonify(new_sponsor.to_dict()), 201

@legacy_bp.route('/profiles/player', methods=['GET'])
def get_player_profiles():
    """
    Get all player profiles
    ---
    tags:
        - Legacy - Profiles
    responses:
        200:
            description: A list of player profiles
    """
    profiles = PlayerProfile.query.all()
    return jsonify([p.to_dict() for p in profiles])

@legacy_bp.route('/profiles/referee', methods=['GET'])
def get_referee_profiles():
    """
    Get all referee profiles
    ---
    tags:
        - Legacy - Profiles
    responses:
        200:
            description: A list of referee profiles
    """
    profiles = RefereeProfile.query.all()
    return jsonify([p.to_dict() for p in profiles])

@legacy_bp.route('/profiles/coach', methods=['GET'])
def get_coach_profiles():
    """
    Get all coach profiles
    ---
    tags:
        - Legacy - Profiles
    responses:
        200:
            description: A list of coach profiles
    """
    profiles = CoachProfile.query.all()
    return jsonify([p.to_dict() for p in profiles])
