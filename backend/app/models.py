from datetime import datetime
from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    graphs = db.relationship('Graph', backref='author', lazy='dynamic')

class Graph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename = db.Column(db.String(140), unique=True)  # 增加唯一约束
    data = db.Column(db.String(256)) 
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    edge_count = db.Column(db.Integer) 

class QueryCache(db.Model):
    id = db.Column(db.String(32), primary_key=True)  # MD5 hash
    result = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)