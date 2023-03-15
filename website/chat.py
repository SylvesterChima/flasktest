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

def is_message_notification(data):
    try:
        if data ["object"]=="page":  #if true hngeeb entry [list]
            for entry in data["entry"]:
                for messaging_event in entry["messaging"]: #3shan ad5ol 3la list 
                    #sender_id = messaging_event["sender"]["id"]
                    #recipient_id = messaging_event["recipient"]["id"] #bgeb mn eldict elrecipient key
                    if messaging_event.get("message"):
                        return True
                    else:
                        return False
        elif data ["object"]=="whatsapp_business_account":
            for entry in data["entry"]:
                for changes_event in entry["changes"]: #3shan ad5ol 3la list 
                    if changes_event["field"] == "messages":
                        return True
                    else:
                        return False
        else:
            return False
    except KeyError:
        return False

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
    mjson = request.get_json()
    logging.error("****** payload ******")
    logging.error(payload)
    logging.error("****** end payload ******")
    logging.error("****** mjson ******")
    logging.error(mjson)
    logging.error("****** end mjson ******")
    logging.error(data)
    if is_message_notification(mjson):
        for entry in mjson["entry"]:
            for messaging_event in entry["messaging"]: #3shan ad5ol 3la list 
                sender_id = messaging_event["sender"]["id"]
                recipient_id = messaging_event["recipient"]["id"] #bgeb mn eldict elrecipient key
                timestamp = messaging_event["timestamp"]

                if "text" in messaging_event["message"]: #key:text 
                    message_id = messaging_event["message"]["mid"]
                    sender_message = messaging_event["message"]["text"] # message text ="hello there"
                    response = {
                        'recipient': {'id': sender_id},
                        "messaging_type": "RESPONSE",
                        "message":{
                            "text": fb_handle_message(sender_id, sender_message)
                        }
                    }
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
    mjson = request.get_json()
    if is_message_notification(mjson):
        for entry in mjson["entry"]:
            for changes in entry["changes"]:
                for messages in entry["value"]["messages"]:
                    message_id = messages["id"]
                    timestamp = messages["timestamp"]
                    message_type = messages["type"]
                    sender = messages["from"]
                    sender_message = messages["text"]["body"]

                    json_data = {"messaging_product": "whatsapp","to": "2348036496516","type": "template",
                    "template": {
                        "name": "hello_world",
                        "language": {
                            "code": "en_US"
                        }
                    }}
                    response = requests.post('https://graph.facebook.com/v16.0/110958208603472/messages?access_token=' + wp_access_token, json=json_data)
    return Response(response="EVENT RECEIVED",status=200)

def wp_handle_message(user_id, user_message):
    # DO SOMETHING with the user_message ... ¯\_(ツ)_/¯
    return "Hello "+user_id+" ! You just sent me : " + user_message
