
from flask import Blueprint, jsonify, request
from app import db
from app.models import Team, Tournament, Post, Comment, Playground, Quest, Achievement, Sponsor, PlayerProfile, RefereeProfile, CoachProfile, User, TeamMembers
from sqlalchemy.orm import joinedload
from flasgger.utils import swag_from

legacy_bp = Blueprint('legacy', __name__)

@legacy_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Legacy'],
    'summary': 'Index route',
    'responses': {
        200: {
            'description': 'Welcome message',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'}
                }
            }
        }
    }
})
def index():
    """Welcome endpoint for the legacy API."""
    return jsonify({'message': 'Welcome to the API!'})

@legacy_bp.route('/tournaments', methods=['GET'])
@swag_from({
    'tags': ['Legacy'],
    'summary': 'Get all tournaments',
    'responses': {
        200: {
            'description': 'A list of tournaments.',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Tournament'}
            }
        }
    }
})
def get_tournaments():
    """Retrieve all tournaments."""
    tournaments = Tournament.query.all()
    return jsonify([t.to_dict() for t in tournaments])

@legacy_bp.route('/tournaments/<int:tournament_id>', methods=['GET'])
@swag_from({
    'tags': ['Legacy'],
    'summary': 'Get a single tournament by ID',
    'parameters': [
        {
            'name': 'tournament_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the tournament to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'Tournament found',
            'schema': {'$ref': '#/definitions/Tournament'}
        },
        404: {'description': 'Tournament not found'}
    }
})
def get_tournament(tournament_id):
    """Retrieve a single tournament by its ID."""
    tournament = db.get_or_404(Tournament, tournament_id)
    return jsonify(tournament.to_dict())

@legacy_bp.route('/tournaments', methods=['POST'])
@swag_from({
    'tags': ['Legacy'],
    'summary': 'Create a new tournament',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'TournamentNew',
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'game': {'type': 'string'},
                    'status': {'type': 'string'},
                    'maxParticipants': {'type': 'integer'},
                    'startDate': {'type': 'string', 'format': 'date-time'}
                },
                'required': ['name', 'game', 'status', 'maxParticipants', 'startDate']
            }
        }
    ],
    'responses': {
        201: {'description': 'Tournament created successfully'},
        400: {'description': 'Missing data'}
    }
})
def create_tournament():
    """Create a new tournament."""
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
@swag_from({
    'tags': ['Legacy'],
    'summary': 'Get all posts',
    'responses': {
        200: {
            'description': 'A list of posts.',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Post'}
            }
        }
    }
})
def get_posts():
    """Retrieve all posts."""
    posts = Post.query.all()
    return jsonify([p.to_dict() for p in posts])

@legacy_bp.route('/posts', methods=['POST'])
@swag_from({
    'tags': ['Legacy'],
    'summary': 'Create a new post',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'PostNew',
                'type': 'object',
                'properties': {
                    'authorId': {'type': 'integer'},
                    'content': {'type': 'string'},
                    'teamId': {'type': 'integer'}
                },
                'required': ['authorId', 'content']
            }
        }
    ],
    'responses': {
        201: {'description': 'Post created successfully'},
        400: {'description': 'Missing data or author/team not found'}
    }
})
def create_post():
    """Create a new post."""
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

# ... Other routes would be documented similarly ...

@legacy_bp.route('/playgrounds', methods=['GET'])
@swag_from({
    'tags': ['Legacy'],
    'summary': 'Get all playgrounds',
    'responses': {
        200: {
            'description': 'A list of playgrounds.',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Playground'}
            }
        }
    }
})
def get_playgrounds():
    playgrounds = Playground.query.all()
    return jsonify([p.to_dict() for p in playgrounds])

@legacy_bp.route('/quests', methods=['GET'])
@swag_from({
    'tags': ['Legacy'],
    'summary': 'Get all quests',
    'responses': {
        200: {
            'description': 'A list of quests.',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Quest'}
            }
        }
    }
})
def get_quests():
    quests = Quest.query.all()
    return jsonify([q.to_dict() for q in quests])

@legacy_bp.route('/achievements', methods=['GET'])
@swag_from({
    'tags': ['Legacy'],
    'summary': 'Get all achievements',
    'responses': {
        200: {
            'description': 'A list of achievements.',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Achievement'}
            }
        }
    }
})
def get_achievements():
    achievements = Achievement.query.all()
    return jsonify([a.to_dict() for a in achievements])

@legacy_bp.route('/sponsors', methods=['GET'])
@swag_from({
    'tags': ['Legacy'],
    'summary': 'Get all sponsors',
    'responses': {
        200: {
            'description': 'A list of sponsors.',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Sponsor'}
            }
        }
    }
})
def get_sponsors():
    sponsors = Sponsor.query.all()
    return jsonify([s.to_dict() for s in sponsors])
