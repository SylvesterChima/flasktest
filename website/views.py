from __future__ import print_function
import uuid
from flask import Blueprint,redirect,url_for,render_template,session,request,flash,current_app,jsonify,Response
from flask_dance.contrib.facebook import facebook
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
from .models import User, CompanyConfig, Company
from . import db
import logging

load_dotenv()
views = Blueprint('views', __name__,)


### WSGI App
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

@views.route('/')
def home():
    session['token'] = uuid.uuid4().hex
    return render_template('index.html', user=current_user)

@views.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'GET':
        logging.error("just a test")
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


@views.route('/configurations', methods=['GET'])
@login_required
def configurations():
    user = User.query.get(current_user.id)
    configs = CompanyConfig.query.filter_by(company_id = user.company_id).all()
    return render_template('configurations.html', configs=configs)

@views.route('/wpconfiguration', methods=['GET', 'POST'])
@login_required
def wpconfiguration():
    if request.method == 'GET':
        user = User.query.get(current_user.id)
        return render_template('wpconfiguration.html')
    else:
        user = User.query.get(current_user.id)
        access_token = request.form.get('AccessToken')
        phone_id = request.form.get('PhoneId')
        app_id = request.form.get('AppId')
        wpa_id = request.form.get('WPAId')
        type = request.form.get('Type')
        phone = request.form.get('Phone')
        config = CompanyConfig(access_token=access_token, phone=phone, phone_id=phone_id,app_id=app_id,wpa_id=wpa_id,type=type, company_id=user.company_id)
        db.session.add(config)
        db.session.commit()
        return redirect(url_for('views.configurations'))

@views.route('/fbconfiguration', methods=['GET'])
def fbconfiguration():
    if not facebook.authorized:
        return redirect(url_for("facebook.login"))
    resp = facebook.get("/me")
    assert resp.ok, resp.text
    return "You are {name} on Facebook".format(name=resp.json()["name"])