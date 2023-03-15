from flask import Blueprint,redirect,url_for,render_template,session,request,flash,current_app,jsonify,Response
import datetime
import requests
import os.path
import os
import json
from dotenv import load_dotenv
import logging

load_dotenv()
chat = Blueprint('chat', __name__,)
verify_token = os.getenv('VERIFY_TOKEN')
fb_access_token = os.getenv('FB_ACCESS_TOKEN')
insta_access_token = os.getenv('INSTA_ACCESS_TOKEN')
wp_access_token = os.getenv('WP_ACCESS_TOKEN')

def is_json_key_present(json, key):
    try:
        buf = json[key]
    except KeyError:
        return False

    return True


# facebook messenger webhook
@chat.route('/webhook', methods=['GET'])
def webhook_verify():
    if request.args.get('hub.verify_token') == verify_token:
        return request.args.get('hub.challenge')
    return verify_token

@chat.route('/webhook', methods=['POST'])
def webhook_action():
    data = json.loads(request.data.decode('utf-8'))
    payload = request.get_data()
    logging.error("****** payload ******")
    logging.error(payload)
    logging.error("****** end payload ******")
    logging.error(data)
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
        response['message']['text'] = fb_handle_message(user_id, user_message)
        r = requests.post('https://graph.facebook.com/v16.0/108409538867050/messages/?access_token=' + fb_access_token, json=response)
    return Response(response="EVENT RECEIVED",status=200)

def fb_handle_message(user_id, user_message):
    # DO SOMETHING with the user_message ... ¯\_(ツ)_/¯
    return "Hello "+user_id+" ! You just sent me : " + user_message


# inatagram messenger webhook
@chat.route('/instagram/webhook', methods=['GET'])
def insta_webhook_verify():
    if request.args.get('hub.verify_token') == verify_token:
        return request.args.get('hub.challenge')
    return verify_token

@chat.route('/instagram/webhook', methods=['POST'])
def insta_webhook_action():
    data = json.loads(request.data.decode('utf-8'))
    logging.error(data)
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
        response['message']['text'] = insta_handle_message(user_id, user_message)
        r = requests.post('https://graph.facebook.com/v16.0/108409538867050/messages/?access_token=' + insta_access_token, json=response)
    return Response(response="EVENT RECEIVED",status=200)

def insta_handle_message(user_id, user_message):
    # DO SOMETHING with the user_message ... ¯\_(ツ)_/¯
    return "Hello "+user_id+" ! You just sent me : " + user_message


# whatsapp messenger webhook
@chat.route('/whatsapp/webhook', methods=['GET'])
def wp_webhook_verify():
    if request.args.get('hub.verify_token') == verify_token:
        return request.args.get('hub.challenge')
    return verify_token

@chat.route('/whatsapp/webhook', methods=['POST'])
def wp_webhook_action():
    data = json.loads(request.data.decode('utf-8'))
    logging.error(data)
    json_data = {"messaging_product": "whatsapp","to": "2348036496516","type": "template",
    "template": {
        "name": "hello_world",
        "language": {
            "code": "en_US"
        }
    }}
    response = requests.post('https://graph.facebook.com/v16.0/110958208603472/messages?access_token=' + insta_access_token, json=json_data)
    return Response(response="EVENT RECEIVED",status=200)

def wp_handle_message(user_id, user_message):
    # DO SOMETHING with the user_message ... ¯\_(ツ)_/¯
    return "Hello "+user_id+" ! You just sent me : " + user_message
