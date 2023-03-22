from flask import Blueprint,redirect,url_for,render_template,session,request,flash,current_app,jsonify,Response,make_response
from .models import User, Conversation, Member, Message
from datetime import datetime
import requests
import os.path
import os
from flask_login import login_user, login_required, logout_user, current_user
import json
from dotenv import load_dotenv
import logging
from sqlalchemy import and_, or_
from . import db

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
                        if changes_event["value"].get("messages"):
                            return True
                        else:
                            return False
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
    mjson = request.get_json()
    if is_message_notification(mjson):
        logging.error("****** fb mjson ******")
        logging.error(mjson)
        logging.error("****** end fb mjson ******")
        for entry in mjson["entry"]:
            for messaging_event in entry["messaging"]: #3shan ad5ol 3la list 
                sender_id = messaging_event["sender"]["id"]
                recipient_id = messaging_event["recipient"]["id"] #bgeb mn eldict elrecipient key
                timestamp = messaging_event["timestamp"]
                datetime_obj = datetime.fromtimestamp(int(timestamp)/1000)

                if "text" in messaging_event["message"]: #key:text 
                    message_id = messaging_event["message"]["mid"]
                    sender_message = messaging_event["message"]["text"] # message text ="hello there"

                    conv=Conversation.query.filter_by(conv_id=sender_id).first()
                    if conv is None:
                        new_conv = Conversation(name=sender_id, conv_id = sender_id, type="fb")
                        db.session.add(new_conv)
                        db.session.commit()

                        member = Member(name=sender_id, mobile_phone = "phone", Conversation_id=new_conv.id)
                        db.session.add(member)
                        member = Member(name="Business", mobile_phone = "Business", Conversation_id=new_conv.id)
                        db.session.add(member)
                        db.session.commit()

                        message = Message(message_id = message_id, message_type="facebook",sender=sender_id, sender_message=sender_message,timestamp=datetime_obj, Conversation_id=new_conv.id, Member_id=member.id)
                        db.session.add(message)
                        db.session.commit()
                        response = {
                            'recipient': {'id': sender_id},
                            "messaging_type": "RESPONSE",
                            "message":{
                                "text": fb_handle_message(sender_id, sender_message)
                            }
                        }
                        r = requests.post('https://graph.facebook.com/v16.0/108409538867050/messages/?access_token=' + fb_access_token, json=response)
                    else:
                        member = Member.query.filter(and_(Member.mobile_phone == "phone", Member.Conversation_id==conv.id)).first()
                        if member:
                            message = Message(message_id = message_id, message_type="facebook",sender=sender_id, sender_message=sender_message,timestamp=datetime_obj, Conversation_id=conv.id, Member_id=member.id)
                            db.session.add(message)
                            db.session.commit()

                        last_message = Message.query.filter(and_(Message.sender == sender_id, Message.Conversation_id==conv.id)).order_by(Message.id.desc()).first()
                        if last_message:
                            hour_difference = (datetime.utcnow() - last_message.timestamp).total_seconds() / 3600
                            if hour_difference >= 24:
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
    return "Hi, how can I help you?"


# inatagram messenger webhook
@chat.route('/instagram/webhook', methods=['GET'])
def insta_webhook_verify():
    if request.args.get('hub.verify_token') == verify_token:
        return request.args.get('hub.challenge')
    return verify_token

@chat.route('/instagram/webhook', methods=['POST'])
def insta_webhook_action():
    mjson = request.get_json()
    logging.error("****** insta mjson ******")
    logging.error(mjson)
    logging.error("****** end insta mjson ******")
    for entry in mjson['entry']:
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
        r = requests.post('https://graph.facebook.com/v16.0/100323863013649/messages/?access_token=' + insta_access_token, json=response)
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
        logging.error("****** wp mjson ******")
        logging.error(mjson)
        logging.error("****** end wp mjson ******")
        for entry in mjson["entry"]:
            for changes in entry["changes"]:
                name = "user"
                for contacts in changes["value"]["contacts"]:
                    name = contacts["profile"]["name"]
                conv_id = changes["value"]["metadata"]["phone_number_id"]
                for messages in changes["value"]["messages"]:
                    message_id = messages["id"]
                    timestamp = messages["timestamp"]
                    message_type = messages["type"]
                    sender = messages["from"]
                    sender_message = messages["text"]["body"]
                    datetime_obj = datetime.fromtimestamp(int(timestamp))

                    conv=Conversation.query.filter_by(conv_id=conv_id).first()
                    if conv is None:
                        new_conv = Conversation(name=name, conv_id = conv_id, type="wp")
                        db.session.add(new_conv)
                        db.session.commit()

                        member = Member(name=name, mobile_phone = sender, Conversation_id=new_conv.id)
                        db.session.add(member)
                        member = Member(name="Business", mobile_phone = "Business", Conversation_id=new_conv.id)
                        db.session.add(member)
                        db.session.commit()

                        message = Message(message_id = message_id, message_type=message_type,sender=sender, sender_message=sender_message,timestamp=datetime_obj, Conversation_id=new_conv.id, Member_id=member.id)
                        db.session.add(message)
                        db.session.commit()
                        json_data = {"messaging_product": "whatsapp","to": sender,"type": "template",
                        "template": {
                            "name": "hello_world",
                            "language": {
                                "code": "en_US"
                            }
                        }}
                        response = requests.post('https://graph.facebook.com/v16.0/110958208603472/messages?access_token=' + wp_access_token, json=json_data)
                    else:
                        member = Member.query.filter(and_(Member.mobile_phone == sender, Member.Conversation_id==conv.id)).first()
                        if member:
                            message = Message(message_id = message_id, message_type=message_type,sender=sender, sender_message=sender_message,timestamp=datetime_obj, Conversation_id=conv.id, Member_id=member.id)
                            db.session.add(message)
                            db.session.commit()

                        last_message = Message.query.filter(and_(Message.sender == sender, Message.Conversation_id==conv.id)).order_by(Message.id.desc()).first()
                        hour_difference = (datetime.utcnow() - last_message.timestamp).total_seconds() / 3600
                        if hour_difference >= 24:
                            json_data = {"messaging_product": "whatsapp","to": sender,"type": "template",
                            "template": {
                                "name": "hello_world",
                                "language": {
                                    "code": "en_US"
                                }
                            }}
                            response = requests.post('https://graph.facebook.com/v16.0/110958208603472/messages?access_token=' + wp_access_token, json=json_data)

    return Response(response="EVENT RECEIVED",status=200)

@chat.route('/whatsapp', methods=['GET'])
@login_required
def whatsapp():
    return render_template('whatsapp.html', user=current_user)

@chat.route('/conversations', methods=['GET'])
def conversations():
    result = []
    conversations = Conversation.query.all()
    for con in conversations:
        new_obj = {
            'id':con.id,
            'name': con.name,
            'conv_id': con.conv_id,
            'type': con.type,
            'date_created': con.date_created
        }
        result.append(new_obj)
    return jsonify(result)

@chat.route('/messages/<int:id>', methods=['GET'])
def messages(id):
    result = []
    messages = Message.query.filter_by(Conversation_id=id).all()
    for con in messages:
        new_obj = {
            'id':con.id,
            'message_id': con.message_id,
            'message_type': con.message_type,
            'sender': con.sender,
            'sender_message': con.sender_message,
            'timestamp': con.timestamp,
            'Conversation_id': con.Conversation_id,
            'Member_id': con.Member_id
        }
        result.append(new_obj)
    return jsonify(result)

@chat.route('/sendmessage', methods=['POST'])
def sendmessage():
    type = request.form.get('type')
    conversationId = request.form.get('conversationId')
    memberId = request.form.get('memberId')
    message = request.form.get('Message')
    recepient = request.form.get('recepient')
    if type == "wp":
        msg = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recepient,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        timestamp = datetime.utcnow()
        response = requests.post('https://graph.facebook.com/v16.0/110958208603472/messages?access_token=' + wp_access_token, json=msg)
        logging.error("****** wp send resp json ******")
        logging.error(response)
        if response.status_code == 200:
            data = json.loads(response.text)
            message_id = data["messages"][0]["id"]
            logging.error(data)
            logging.error("****** wp send resp json ******")
            messageObj = Message(message_id = message_id, message_type="text",sender="Business", sender_message=message,timestamp=timestamp, Conversation_id=conversationId, Member_id=memberId)
            db.session.add(messageObj)
            db.session.commit()
            new_obj = {
                'id':messageObj.id,
                'message_id': message_id,
                'message_type': "text",
                'sender': "Business",
                'sender_message': message,
                'timestamp': timestamp,
                'Conversation_id': conversationId,
                'Member_id': memberId
            }
            resp = make_response(new_obj)
            resp.status_code = 200
            return resp
        else:
            resp = make_response("message failed")
            resp.status_code = 400
            return resp
    else:
        resp = make_response("message failed")
        resp.status_code = 400
        return resp
























def wp_handle_message(user_id, user_message):
    # DO SOMETHING with the user_message ... ¯\_(ツ)_/¯
    return "Hello "+user_id+" ! You just sent me : " + user_message
