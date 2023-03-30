from . import db
from flask_login import UserMixin
from datetime import datetime
# from sqlalchemy.sql import func



class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    website = db.Column(db.String(500))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    conversations = db.relationship('Conversation',backref='company')
    company_configs = db.relationship('CompanyConfig',backref='company')
    users = db.relationship('User',backref='company')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    mobile_phone = db.Column(db.String(15))
    address = db.Column(db.String(500))
    profile_image = db.Column(db.String(2000))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'),nullable=False)

class CompanyConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    page_id= db.Column(db.String())
    page_name= db.Column(db.String())
    phone = db.Column(db.String(15))
    phone_id = db.Column(db.String())
    app_id = db.Column(db.String())
    wpa_id = db.Column(db.String())
    access_token = db.Column(db.String())
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'),nullable=False)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    conv_id = db.Column(db.String(200))
    page_id = db.Column(db.String(200))
    type = db.Column(db.String(50))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'),nullable=False)
    messages = db.relationship('Message',backref='conversation')
    members = db.relationship('Member',backref='conversation')


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    mobile_phone = db.Column(db.String())
    Conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'),nullable=False)
    messages = db.relationship('Message',backref='member')


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String())
    message_type = db.Column(db.String())
    sender = db.Column(db.String())
    sender_message=db.Column(db.String())
    timestamp = db.Column(db.DateTime)
    Conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'),nullable=False)
    Member_id = db.Column(db.Integer, db.ForeignKey('member.id'),nullable=False)
