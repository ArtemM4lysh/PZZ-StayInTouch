from datetime import datetime
from email.policy import default
from enum import unique, Enum

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
    pesel = db.Column(db.String(265), nullable=False, unique=True)
    phone_number = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150))
    name = db.Column(db.String(150), nullable=False)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    last_visit_id = db.Column(db.Integer)
    last_date_of_visit = db.Column(db.DateTime, default=datetime.now)
    total_visits = db.Column(db.Integer)


class RoomType(Enum):
    VIP = "VIP"
    BUSINESS = "Business"
    BUDGET = "Budget"


class Visits(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    check_in_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    check_out_date = db.Column(db.DateTime)
    hotel_id = db.Column(db.Integer, nullable=False)
    room_type = db.Column(db.Enum(RoomType), nullable=False)


class CampaignStatus(Enum):
    DRAFT = "Draft"
    SENT = "Sent"
    SCHEDULED = "Scheduled"
    FAILED = "Failed"


class EmailCampaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    sent_at = db.Column(db.DateTime)
    total_recipients = db.Column(db.Integer, default=0)
    successful_sends = db.Column(db.Integer, default=0)
    failed_sends = db.Column(db.Integer, default=0)

    # Relationship
    creator = db.relationship('User', backref='campaigns')


class CampaignRecipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('email_campaign.id'), nullable=False)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitor.id'), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    sent_at = db.Column(db.DateTime)
    delivery_status = db.Column(db.String(50), default='pending')  # pending, sent, failed
    error_message = db.Column(db.Text)

    # Relationships
    campaign = db.relationship('EmailCampaign', backref='recipients')
    visitor = db.relationship('Visitor', backref='campaign_recipients')