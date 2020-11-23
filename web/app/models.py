import datetime

import jwt

from app import db, SECRET_KEY

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(64), unique=True)
    
    login = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))
    
    admin = db.Column(db.Boolean)

    rating = db.Column(db.Integer)

    def convert_to_dict(self):
        return {
            'public_id': self.public_id,
            'login': self.login,
            'admin': self.admin,
            'rating': self.rating
        }

    def encode_auth_token(self):
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=30),
            'iat': datetime.datetime.utcnow(),
            'user': {
                'public_id': self.public_id,
                'login': self.login
            }
        }
        return jwt.encode(
            payload=payload,
            key=SECRET_KEY,
            algorithm='HS256'
        )
