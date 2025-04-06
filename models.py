from datetime import datetime

from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __init__(self, username, email, password_hash):
        self.username = username
        self.email = email
        self.password_hash = password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pesel = db.Column(db.Integer, nullable=False, unique=True)
    phone_number = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150))
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    last_date_of_visit = db.Column(db.DateTime, default=datetime.now)
    total_visits = db.Column(db.Integer)
