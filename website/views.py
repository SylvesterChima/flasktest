from __future__ import print_function
import uuid
from flask import Blueprint,redirect,url_for,render_template,session,request,flash,current_app,jsonify,Response
import datetime
import requests
import os.path
import os
import json
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from .models import User
from . import db

load_dotenv()
views = Blueprint('views', __name__,)
# token to verify that this bot is legit
os.environ['VERIFY_TOKEN'] = 'yess'
verify_token = os.getenv('VERIFY_TOKEN')
# token to send messages through facebook messenger
access_token = os.getenv('PAGE_ACCESS_TOKEN')
access_token2 = os.environ['PAGE_ACCESS_TOKEN']

### WSGI App
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

@views.route('/')
def home():
    session['token'] = uuid.uuid4().hex
    return render_template('index.html', user=current_user)

@views.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'GET':
        session['token'] = uuid.uuid4().hex
        return render_template('feedback.html', user=current_user,message="")
    else:
        wp_token = os.getenv("wp_token")
        message = request.form.get('Message')
        json_data = {"messaging_product": "whatsapp","to": "2348036496516","type": "template",
        "template": {
            "name": "hello_world",
            "language": {
                "code": "en_US"
            }
        }}
        headers = {
            'Authorization': f'Bearer ' + wp_token,
            'Content-Type': 'application/json'
        }
        response = requests.post("https://graph.facebook.com/v15.0/110958208603472/messages", headers=headers, json=json_data)
        return render_template('feedback.html', user=current_user, message=message)

@views.route('/webhook', methods=['GET'])
def webhook_verify():
    if request.args.get('hub.verify_token') == verify_token:
        return request.args.get('hub.challenge')
    return verify_token + " and " + access_token2

@views.route('/webhook', methods=['POST'])
def webhook_action():
    data = json.loads(request.data.decode('utf-8'))
    print(data)
    for entry in data['entry']:
        user_message = entry['messaging'][0]['message']['text']
        user_id = entry['messaging'][0]['sender']['id']
        response = {
            'recipient': {'id': user_id},
            "messaging_type": "RESPONSE",
            "message":{
                "text":"Hello, world!"
            }
        }
        response['message']['text'] = handle_message(user_id, user_message)
        r = requests.post('https://graph.facebook.com/v16.0/108409538867050/messages/?access_token=' + access_token, json=response)
    return Response(response="EVENT RECEIVED",status=200)

def handle_message(user_id, user_message):
    # DO SOMETHING with the user_message ... ??\_(???)_/??
    return "Hello "+user_id+" ! You just sent me : " + user_message

@views.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    session.pop('_flashes', None)
    if request.method == 'POST':
        FirstName = request.form.get('FirstName')
        LastName = request.form.get('LastName')
        MobileNumber = request.form.get('MobileNumber')
        Address = request.form.get('Address')
        user = User.query.get(current_user.id)
        user.last_name = LastName
        user.first_name = FirstName
        user.mobile_phone = MobileNumber
        user.address = Address
        db.session.commit()
        flash('Profile updated!', category='success')
    return render_template('profile.html', user=current_user)

@views.route('/api_profile', methods=['POST'])
@login_required
def api_profile():
    file = request.files['ProfileImage']
    if file.filename != '':
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    user = User.query.get(current_user.id)
    user.profile_image = filename
    db.session.commit()
    return redirect(url_for('views.profile')) 

@views.route('/events')
@login_required
def events():
    creds = None
    tokenName = session['token']
    if os.path.exists(str(tokenName) + 'token.json'):
        creds = Credentials.from_authorized_user_file(str(tokenName) + 'token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(str(tokenName) + 'token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(calendarId='primary', timeMax=now,
                                              maxResults=100, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            return render_template('events.html', events = events)

    except HttpError as error:
        print('An error occurred: %s' % error)

