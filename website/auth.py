import pathlib
from  flask import Blueprint,redirect,url_for,render_template,request,flash,session,abort,current_app,jsonify
from .models import User, Company
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import os
import requests
from pip._vendor import cachecontrol
from flask_oauthlib.client import OAuth
#import pyrebase

firebaseConfig = {
  'apiKey': "AIzaSyBiUgJSOVKEDZgqhEUp18fIFEUek5Bl0wg",
  'authDomain': "authdemo-c09f5.firebaseapp.com",
  'projectId': "authdemo-c09f5",
  'storageBucket': "authdemo-c09f5.appspot.com",
  'messagingSenderId': "729649386175",
  'appId': "1:729649386175:web:5d22172dc8a501cccdec0a",
  'measurementId': "G-LBZJB80TC5",
  'databaseURL': ''
}

auth = Blueprint('auth', __name__,)
oauth = OAuth(current_app)
#firebase = pyrebase.initialize_app(firebaseConfig)
#mAuth = firebase.auth()



#Google
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = "74510656303-qplvmj3ikm06scjeegkd59s2vo5p8nhf.apps.googleusercontent.com"
client_secrets_file = "client_secret.json"

# flow = Flow.from_client_secrets_file(
#     client_secrets_file=client_secrets_file,
#     scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
#     redirect_uri="http://127.0.0.1:5000/callback"
# )

#Linkedin
# linkedin = oauth.remote_app(
#     'linkedin',
#     consumer_key='77z696pencgm4l',
#     consumer_secret='SbE1XJ30MUoKSy8q',
#     request_token_params={
#         'scope': 'r_liteprofile r_emailaddress'
#     },
#     base_url='https://api.linkedin.com/v2/',
#     request_token_url=None,
#     access_token_method='POST',
#     access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
#     authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
# )



# @auth.route("/googlelogin")
# def googlelogin():
#     authorization_url, state = flow.authorization_url()
#     session["state"] = state
#     return redirect(authorization_url)


# @auth.route("/callback")
# def callback():
#     flow.fetch_token(authorization_response=request.url)

#     if not session["state"] == request.args["state"]:
#         return redirect(url_for('auth.login'))

#     credentials = flow.credentials
#     request_session = requests.session()
#     cached_session = cachecontrol.CacheControl(request_session)
#     token_request = google.auth.transport.requests.Request(session=cached_session)

#     id_info = id_token.verify_oauth2_token(
#         id_token=credentials._id_token,
#         request=token_request,
#         audience=GOOGLE_CLIENT_ID
#     )
#     email = id_info.get("email")
#     first_name = id_info.get("given_name")
#     last_name = id_info.get("family_name")
#     password1 = id_info.get("at_hash")
#     profile_image = id_info.get("profile_image")

#     user = User.query.filter_by(email=email).first()
#     if user:
#         login_user(user, remember=True)
#     else:
#         new_user = User(email=email, first_name=first_name, last_name = last_name, profile_image=profile_image, password=generate_password_hash(password1, method='sha256'))
#         db.session.add(new_user)
#         db.session.commit()
#         login_user(new_user, remember=True)

#     return redirect(url_for('views.dashboard'))


# @auth.route('/linkedinlogin')
# def linkedinlogin():
#     return linkedin.authorize(callback=url_for('auth.authorized', _external=True))

# @auth.route('/authorized')
# def authorized():
#     resp = linkedin.authorized_response()
#     if resp is None:
#         return redirect(url_for('auth.login'))
#     session['linkedin_token'] = (resp['access_token'], '')
#     me = linkedin.get('me')
#     emailAddress = linkedin.get('emailAddress?q=members&projection=(elements*(handle~))')

#     email = emailAddress.data.get("elements")[0].get("handle~").get("emailAddress")
#     first_name = me.data.get('localizedFirstName')
#     last_name = me.data.get('localizedLastName')
#     password1 = me.data.get('id')
#     profile_image = "user.png"

#     user = User.query.filter_by(email=email).first()
#     if user:
#         login_user(user, remember=True)
#     else:
#         new_user = User(email=email, first_name=first_name, last_name = last_name, profile_image=profile_image, password=generate_password_hash(password1, method='sha256'))
#         db.session.add(new_user)
#         db.session.commit()
#         login_user(new_user, remember=True)

#     return redirect(url_for('views.dashboard'))

# @linkedin.tokengetter
# def get_linkedin_oauth_token():
#     return session.get('linkedin_token')


# def change_linkedin_query(uri, headers, body):
#     auth = headers.pop('Authorization')
#     headers['x-li-format'] = 'json'
#     if auth:
#         auth = auth.replace('Bearer', '').strip()
#         if '?' in uri:
#             uri += '&oauth2_access_token=' + auth
#         else:
#             uri += '?oauth2_access_token=' + auth
#     return uri, headers, body

# linkedin.pre_request = change_linkedin_query

# @auth.route("/resetpassword", methods=['GET', 'POST'] )
# def resetpassword():
#     try:
#         if request.method == 'POST':
#             password = request.form.get('Password')
#             code = request.form.get('code')
#             result = mAuth.verify_password_reset_code(code,password)

#             return result
#         else:
#             code = request.args.get('oobCode')
#             return render_template("resetpassword.html", oocode = code)
#     except Exception as error:
#         current_app.logger.exception(error)
#         return str(error)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    try:
        session.pop('_flashes', None)
        if request.method == 'POST':
            email = request.form.get('Email')
            password = request.form.get('Password')

            user = User.query.filter_by(email=email).first()
            if user:
                if check_password_hash(user.password, password):
                    flash('Logged in successfully!', category='success')
                    login_user(user, remember=True)
                    return redirect(url_for('views.dashboard'))
                else:
                    flash('Incorrect password, try again.', category='error')
            else:
                flash('Email does not exist.', category='error')
        #result = mAuth.sign_in_with_email_and_password('sylvesterchima11@outlook.com','ss123456')
        #return result
        return render_template('login.html')
    except Exception as error:
        current_app.logger.exception(error)
        flash(str(error), category='error')
        return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    tokenName = session['token']
    if os.path.exists(str(tokenName) + 'token.json'):
        os.remove(str(tokenName) + 'token.json')
    session.pop('state', None)
    session.clear()
    logout_user()
    return redirect(url_for('views.home'))


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    session.pop('_flashes', None)
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        business_name = request.form.get('BusinessName')
        website = request.form.get('Website')
        email = request.form.get('Email')
        first_name = request.form.get('FirstName')
        last_name = request.form.get('LastName')
        password1 = request.form.get('Password1')
        password2 = request.form.get('Password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            company = Company(name=business_name, website=website)
            db.session.add(company)
            db.session.commit() 
            new_user = User(email=email, first_name=first_name, last_name = last_name, profile_image='user.png', password=generate_password_hash(password1, method='sha256'), company_id = company.id)
            db.session.add(new_user)
            db.session.commit() 
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.dashboard'))

        return render_template('signup.html')
