from __future__ import print_function
import uuid
import nanoid
from flask import Blueprint,redirect,url_for,render_template,session,request,flash,current_app,jsonify,Response,make_response
import datetime
import requests
import os.path
import os
import json
from dotenv import load_dotenv
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from .models import User, CompanyConfig, Company
from . import db
import logging
from paystackapi.paystack import Paystack
paystack_secret_key = "sk_test_bb61240a97e7edc389182ae173fbeff5e97c27f5"
paystack = Paystack(secret_key=paystack_secret_key)
from paystackapi.transaction import Transaction
from paystackapi.transaction_split import TransactionSplit


load_dotenv()
views = Blueprint('views', __name__,)


### WSGI App
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

@views.route('/trypayment', methods=['GET'])
def test_initialize_transaction():
    generated_ref = nanoid.generate()
    ref_code = str(generated_ref)
    response = Transaction.initialize(reference=ref_code, amount='10000', email='chima@troolog.com', subaccount = 'ACCT_evvm9erp1whhwsh')
    print(response)
    return redirect(response["data"]["authorization_url"])

@views.route('/splitpayment', methods=['GET'])
def test_initialize_split_transaction():
    generated_ref = nanoid.generate()
    ref_code = str(generated_ref)
    response = TransactionSplit.create(
            name="EZE SYLVESTER CHIMA",
            type="percentage",
            currency="NGN",
            subaccounts=[{'subaccount': 'ACCT_evvm9erp1whhwsh', 'share':95 }],
            bearer_type="account"
        )
    print(response)
    return redirect(response["data"]["authorization_url"])

@views.route('/paymentcallback', methods=['GET'])
def payment_callback():
    ref = request.args.get('reference')
    #response = Transaction.verify(ref);
    return ref


@views.route('/')
def home():
    session['token'] = uuid.uuid4().hex
    logging.error("home")
    if 'chatsession' not in session:
        session['chatsession'] = nanoid.generate()
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
    logging.error("dashboard")
    return render_template('dashboard.html')

@views.route('/privacy')
def privacy():
    return render_template('privacy.html', user=current_user)

@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    session.pop('_flashes', None)
    logging.error("profile")
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


@views.route('/configurations', methods=['GET'])
@login_required
def configurations():
    configId = os.getenv('FACEBOOK_CONFIG_ID')
    app_id = os.getenv('FACEBOOK_OAUTH_CLIENT_ID')
    app_secret = os.getenv('FACEBOOK_OAUTH_CLIENT_SECRET')
    user = User.query.get(current_user.id)
    configs = CompanyConfig.query.filter_by(company_id = user.company_id).all()
    insta_login = "https://www.facebook.com/v16.0/dialog/oauth?client_id=" + app_id + "&display=page&extras={\"setup\":{\"channel\":\"PARTNER\"}}&redirect_uri=https://troolog.azurewebsites.net/instaconfiguration&response_type=token&scope=instagram_basic,instagram_manage_messages,pages_manage_metadata"
    return render_template('configurations.html', configs=configs, configId=configId,userId=current_user.id, app_id=app_id, app_secret=app_secret,insta_login = insta_login )

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

@views.route('/fbconfiguration', methods=['POST'])
def fbconfiguration():
    data = request.get_json()
    userId = data['userId']
    user = User.query.get(userId)
    pages = data['data']
    type = data['type']
    llat = data['llat']
    for page in pages:
        response = requests.get('https://graph.facebook.com/'+ page['id'] +'?fields=access_token&access_token=' + llat)
        pData = json.loads(response.text)
        logging.info("****** permanent access token mjson ******")
        logging.info(pData)
        if response.status_code == 200:
            config = CompanyConfig(access_token=pData['access_token'], page_id=page['id'],type=type, page_name=page['name'], company_id=user.company_id)
            db.session.add(config)
            db.session.commit()

            r = requests.post('https://graph.facebook.com/'+ page['id'] + '/subscribed_apps?subscribed_fields=messages,message_reads,message_reactions,messaging_postbacks,message_deliveries&access_token='+ pData['access_token'])
            data1 = json.loads(r.text)
            logging.info("****** subscribed_apps sent mjson ******")
            logging.info(data1)

    new_obj = {
        'message': "Added successful"
    }
    resp = make_response(new_obj)
    resp.status_code = 200
    return resp

@views.route('/configinstagram/<string:longtoken>', methods=['GET'])
def configinstagram(longtoken):
    print(longtoken)
    user = User.query.get(current_user.id)
    response = requests.get('https://graph.facebook.com/v16.0/me/accounts?fields=id%2Caccess_token%2Cname%2Cinstagram_business_account&access_token=' + longtoken)
    data = json.loads(response.text)
    logging.info("****** me/accounts ******")
    logging.info(data)
    print(data)

    for page in data['data']:
        response = requests.get('https://graph.facebook.com/'+ page['id'] +'?fields=access_token&access_token=' + longtoken)
        pData = json.loads(response.text)
        logging.info("****** permanent access token mjson ******")
        logging.info(pData)
        print(pData)
        if response.status_code == 200:
            if "instagram_business_account" in page:
                config = CompanyConfig(access_token=pData['access_token'], phone_id=page['instagram_business_account']['id'],page_id=page['id'],type="insta", page_name=page['name'], company_id=user.company_id)
                db.session.add(config)
                db.session.commit()

                r = requests.post('https://graph.facebook.com/'+ page['id'] + '/subscribed_apps?subscribed_fields=feed&access_token='+ pData['access_token'])
                data1 = json.loads(r.text)
                logging.info("****** subscribed_apps sent mjson ******")
                logging.info(data1)
                print(data1)

    resp = make_response("Connected")
    resp.status_code = 200
    return resp
    #return redirect(url_for('views.configurations'))


@views.route('/instaconfiguration', methods=['GET'])
def instaconfiguration():
    baseUrl = os.getenv('BASEURL')
    return render_template('instaconfiguration.html',baseUrl=baseUrl)


@views.route('/test')
def test():
    company = Company.query.get(current_user.company_id)
    return render_template('test.html', user=current_user, company = company)