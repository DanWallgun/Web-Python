import uuid
import datetime
import random

from functools import wraps

import jwt
from flask import jsonify, request, render_template, abort, redirect
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import User
from app import app, db

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' not in request.headers:
            response = {
                'errors': [
                    {'message': 'No authorization header'}
                ]
            }
            return jsonify(response), 401
        elif len(request.headers['Authorization']) < len('Bearer '):
            response = {
                'errors': [
                    {'message': 'Invalid authorization header'}
                ]
            }
            return jsonify(response), 401
        
        token = request.headers['Authorization'].split()[1]

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=payload['user']['public_id']).first()
        except:
            response = {
                'errors': [
                    {'message': 'Invalid token'}
                ]
            }
            return jsonify(response), 401
        
        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/api/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    users = User.query.all()

    response = {
        'users': []
    }

    for user in users:
        response['users'].append(user.convert_to_dict())

    return jsonify(response)


@app.route('/api/user/<public_id>', methods=['GET'])
def get_one_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        user = User.query.filter_by(login=public_id).first()

    if not user:
        response = {
            'errors': [
                {'message': 'User is not found'}
            ]
        }
        return jsonify(response), 400

    return jsonify({'user': user.convert_to_dict()})


@app.route('/api/user', methods=['POST'])
def create_user():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(
        public_id=str(uuid.uuid4()),
        login=data['login'],
        password=hashed_password,
        admin=False,
        rating=1400
    )

    try:
        db.session.add(new_user)
        db.session.commit()
    except:
        return jsonify({
            'errors': [
                {'message': 'Error while creating user'}
            ]
        })

    return jsonify({'user': new_user.convert_to_dict()})


@app.route('/api/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        response = {
            'errors': [
                {'message': 'User is not found'}
            ]
        }
        # Bad Request
        return jsonify(response), 400
    else:
        db.session.delete(user)
        return jsonify({})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if 'login' not in data or 'password' not in data:
        response = {
            'errors': [
                {'message': 'Insufficient data for authorization'}
            ]
        }
        # Bad Request
        return jsonify(response), 400
    
    user = User.query.filter_by(login=data['login']).first()
    if not user:
        response = {
            'errors': [
                {'message': 'User is not found'}
            ]
        }
        # Bad Request
        return jsonify(response), 400
    
    if not check_password_hash(user.password, data['password']):
        response = {
            'errors': [
                {'message': 'Wrong password'}
            ]
        }
        # Bad Request
        return jsonify(response), 400

    try:
        token = user.encode_auth_token()
        return jsonify({
            'token': token.decode('UTF-8')
        })
    except:
        abort(500)


@app.route('/api/battle', methods=['POST'])
@token_required
def api_battle(current_user):
    data = request.get_json()
    if 'user' not in data or 'login' not in data['user']:
        response = {
            'errors': [
                {'message': 'User is not found'}
            ]
        }
        # Bad Request
        return jsonify(response), 400
    
    user = User.query.filter_by(login=data['user']['login']).first()
    if not user:
        response = {
            'errors': [
                {'message': 'User is not found'}
            ]
        }
        # Bad Request
        return jsonify(response), 400

    if user.public_id == current_user.public_id:
        response = {
            'errors': [
                {'message': 'Opponents cannot match'}
            ]
        }
        # Bad Request
        return jsonify(response), 400

    random.seed(datetime.datetime.utcnow())
    dice_a = random.randint(1, 6)
    dice_b = random.randint(1, 6)

    def EloRating(rating_a, rating_b, score_a, score_b):
        expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
        expected_b = 1 / (1 + 10 ** ((rating_a - rating_b) / 400))
        k = 16
        return rating_a + k * (score_a - expected_a), \
               rating_b + k * (score_b - expected_b)
    
    score_a = 0.5
    score_b = 0.5
    if dice_a > dice_b:
        score_a = 1
        score_b = 0
    elif dice_a < dice_b: 
        score_a = 0
        score_b = 1
    current_user.rating, user.rating = \
        map(int, EloRating(current_user.rating, user.rating, score_a, score_b))
    db.session.commit()
    
    return jsonify({
        'dices': [dice_a, dice_b],
    })


@app.route('/')
def index():
    users = User.query.order_by(desc('rating'))

    return render_template('index.html', title='Home', users=users)


@app.route('/profile/<public_id>')
def profile(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return redirect('/')

    return render_template('profile.html', title=user.login, user=user)


@app.route('/login')
def login():
    return render_template('login.html', title='Login')


@app.route('/register')
def register():
    return render_template('register.html', title='Register')


@app.route('/battle')
def battle():
    return render_template('battle.html', title='Battle')
