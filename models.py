from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

db = SQLAlchemy()

saved = db.Table('saved',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('game_name', db.String, db.ForeignKey('game.name'), primary_key=True)
)

class Game(db.Model):
    __tablename__ = 'game'
    id = db.Column(db.Integer)
    name = db.Column(db.String, primary_key=True)
    date = db.Column(db.String)
    platform = db.Column(db.String)
    score = db.Column(db.Float)
    url = db.Column(db.String)
    userscore = db.Column(db.Float)
    genre = db.Column(db.String)
    savedby = db.relationship('User', secondary=saved, lazy = 'dynamic', backref=db.backref('saved', lazy=True))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True)

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)

'''
class saved(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, foreign_key=True)
    user = db.Column(db.String, foreign_key=True)

    def __init__(self, name, user):
        self.name = name
        self.user = user
'''

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)