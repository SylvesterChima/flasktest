from sched import scheduler
from flask import Flask
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_sqlalchemy import SQLAlchemy
from os import path
import os
from flask_login import LoginManager
from flask_apscheduler import APScheduler
from dotenv import load_dotenv
import urllib
import logging
import pyodbc

load_dotenv()
scheduler = APScheduler()
db = SQLAlchemy()
#facebook_bp = None
uri = urllib.parse.quote_plus("Driver=ODBC+Driver+18+for+SQL+Server;Server=tcp:troologserver.database.windows.net,1433;Database=troologdata;Uid=troolog;Pwd=@Admin12;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")
UPLOAD_FOLDER = 'website/static/uploads/'
ENV = os.getenv("STAGE")
def create_app():
    app = Flask(__name__)
    logging.basicConfig(level=logging.INFO, format=f'%(asctime)s %(levelname)s %(name)s : %(message)s')
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersekrit")
    app.config['SECRET_KEY'] = 'hjhjhjhjhdhjhdhjhgsjkhdshds'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config["FACEBOOK_OAUTH_CLIENT_ID"] = os.getenv("FACEBOOK_OAUTH_CLIENT_ID")
    app.config["FACEBOOK_OAUTH_CLIENT_SECRET"] = os.getenv("FACEBOOK_OAUTH_CLIENT_SECRET")
    app.config["OAUTHLIB_INSECURE_TRANSPORT"] = "true"
    if ENV == 'dev':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/demodata'
        #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
    else:
        #app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://dflask:@Standup12@dflask-server.database.windows.net/dflask_data?driver=ODBC+Driver+17+for+SQL+Server'
        #app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % uri
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://vcoibczjbx:H2D8UYTZ582Z3OOU$@troologdemo-server.postgres.database.azure.com/troologdemo-database?sslmode=require'

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    #with app.app_context():
    #    db.init_app(app)

    db.init_app(app)



    from .views import views
    from .auth import auth
    from .chat import chat

    app.register_blueprint(views)
    app.register_blueprint(auth)
    app.register_blueprint(chat)

    facebook_bp = make_facebook_blueprint()
    app.register_blueprint(facebook_bp, url_prefix="/fbconfiguration")

    from .models import User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    #send_email_job(app)

    return app

def send_email():
    print("email sent!!!!")

def send_reminder():
    print("Reminder sent!!!!")

def create_database(app):
    # if not path.exists('website/' + DB_NAME):
    #     db.create_all(app=app)
    with app.app_context():
        db.create_all()
    print('Created Database!')

def send_email_job(app):
    scheduler.add_job(id = 'send email', func= send_email, trigger = 'interval', seconds = 5)
    scheduler.add_job(id = 'send reminder', func= send_reminder, trigger = 'interval', seconds = 8)
    scheduler.start()
    print('Job Started')


