from . import db
from flask_login import UserMixin
from datetime import datetime
from dataclasses import dataclass
# from sqlalchemy.sql import func


@dataclass
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    mobile_phone = db.Column(db.String(15))
    address = db.Column(db.String(500))
    profile_image = db.Column(db.String(2000))

@dataclass
class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    conv_id = db.Column(db.String(200))
    type = db.Column(db.String(50))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message',backref='conversation')
    members = db.relationship('Member',backref='conversation')


@dataclass
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    mobile_phone = db.Column(db.String(15))
    Conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'),nullable=False)
    messages = db.relationship('Message',backref='member')


@dataclass
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String())
    message_type = db.Column(db.String())
    sender = db.Column(db.String())
    sender_message=db.Column(db.String())
    timestamp = db.Column(db.DateTime)
    Conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'),nullable=False)
    Member_id = db.Column(db.Integer, db.ForeignKey('member.id'),nullable=False)
