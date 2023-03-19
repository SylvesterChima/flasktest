from sched import scheduler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_apscheduler import APScheduler
import urllib
import logging
import pyodbc

scheduler = APScheduler()
db = SQLAlchemy()
uri = urllib.parse.quote_plus("Driver=ODBC+Driver+18+for+SQL+Server;Server=tcp:troologserver.database.windows.net,1433;Database=troologdata;Uid=troolog;Pwd=@Admin12;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")
UPLOAD_FOLDER = 'website/static/uploads/'
ENV = 'prod'
def create_app():
    app = Flask(__name__)
    logging.basicConfig(format=f'%(asctime)s %(levelname)s %(name)s : %(message)s')
    app.config['SECRET_KEY'] = 'hjhjhjhjhdhjhdhjhgsjkhdshds'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    if ENV == 'dev':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/demodata'
        #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
    else:
        #app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://dflask:@Standup12@dflask-server.database.windows.net/dflask_data?driver=ODBC+Driver+17+for+SQL+Server'
        #app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % uri
        app.config[''] = 'postgresql://vcoibczjbx:H2D8UYTZ582Z3OOU$@troologdemo-server.postgres.database.azure.com/rtroologdemo-database?sslmode=require'

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    #with app.app_context():
    #    db.init_app(app)

    db.init_app(app)



    from .views import views
    from .auth import auth
    from .chat import chat

    app.register_blueprint(views, url_prfix='/')
    app.register_blueprint(auth, url_prfix='/')
    app.register_blueprint(chat, url_prfix='/')

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
    db.create_all(app=app)
    print('Created Database!')

def send_email_job(app):
    scheduler.add_job(id = 'send email', func= send_email, trigger = 'interval', seconds = 5)
    scheduler.add_job(id = 'send reminder', func= send_reminder, trigger = 'interval', seconds = 8)
    scheduler.start()
    print('Job Started')


