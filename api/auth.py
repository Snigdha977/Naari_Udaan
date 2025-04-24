from flask import Blueprint, request, jsonify, session
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    full_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

auth_bp = Blueprint('auth', __name__)

# Your Google OAuth 2.0 Client ID
CLIENT_ID = '647768749306-m8ocoj8f7kocbh103u7b021ch76gt9k0.apps.googleusercontent.com'

@auth_bp.route('/auth/google', methods=['POST'])
def google_auth():
    try:
        # Get the token from the request
        token = request.json.get('credential')
        
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), CLIENT_ID)
            
        # Get user info from the token
        user_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo['name']
        
        # Check if user exists in database
        user = User.query.filter_by(google_id=user_id).first()
        
        if not user:
            # Create new user
            new_user = User(
                google_id=user_id,
                email=email,
                full_name=name,
                created_at=datetime.utcnow()
            )
            db.session.add(new_user)
            db.session.commit()
            user = new_user
        
        # Create session
        session['user_id'] = user.id
        session['logged_in'] = True
        
        return jsonify({
            'success': True,
            'user': {
                'id': user_id,
                'email': email,
                'name': name
            }
        })
        
    except ValueError as e:
        # Invalid token
        return jsonify({
            'success': False,
            'error': str(e)
        }), 401