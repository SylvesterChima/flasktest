from . import db
from flask_login import UserMixin
# from sqlalchemy.sql import func



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    mobile_phone = db.Column(db.String(15))
    address = db.Column(db.String(500))
    profile_image = db.Column(db.String(2000))