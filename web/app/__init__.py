import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'tXPG0QknXXmu4gtHGxiqNCHP0BFgAX8Kfdqt4Y900Y16jh43LXnC6RVdTMtIzehC'
)
SQLALCHEMY_DATABASE_URI = os.getenv(
    'SQLALCHEMY_DATABASE_URI',
    'sqlite:///./main.db'
)

app.config['SECRET_KEY'] = SECRET_KEY 
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

db = SQLAlchemy(app)

from app import routes, models

db.create_all()