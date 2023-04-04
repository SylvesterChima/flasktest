from flask import Blueprint,redirect,url_for,render_template,session,request,flash,current_app,jsonify,Response,make_response
from .models import User, Conversation, Member, Message, Company, CompanyConfig
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
insta_access_token = os.getenv('INSTA_ACCESS_TOKEN')

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
    except Exception as e:
        logging.error(str(e))
        return False

@chat.route('/deleteall', methods=['GET'])
def deleteAll():
    db.session.query(Message).delete()
    db.session.commit()
    db.session.query(Member).delete()
    db.session.commit()
    db.session.query(Conversation).delete()
    db.session.commit()
    db.session.query(CompanyConfig).delete()
    db.session.commit()
    db.session.query(User).delete()
    db.session.commit()
    db.session.query(Company).delete()
    db.session.commit()
    return redirect(url_for('chat.chatapp'))

def get_userinfo(pSID, accessToken):
    response = requests.get('https://graph.facebook.com/v16.0/'+ pSID + '?access_token=' + accessToken)
    if response.status_code == 200:
        data = json.loads(response.text)
        print(data)
        return data
    else:
        data = {
            'last_name': pSID,
            "first_name": ""
        }
        return data

# facebook messenger webhook
@chat.route('/webhook', methods=['GET'])
def webhook_verify():
    if request.args.get('hub.verify_token') == verify_token:
        return request.args.get('hub.challenge')
    return verify_token

@chat.route('/webhook', methods=['POST'])
def webhook_action():
    try:
        mjson = request.get_json()
        logging.info("****** fb mjson ******")
        logging.info(mjson)
        logging.info("****** end fb mjson ******")
        if is_message_notification(mjson):

            for entry in mjson["entry"]:
                page_id = entry["id"]
                for messaging_event in entry["messaging"]:
                    sender_id = messaging_event["sender"]["id"]
                    recipient_id = messaging_event["recipient"]["id"] #bgeb mn eldict elrecipient key
                    timestamp = messaging_event["timestamp"]
                    datetime_obj = datetime.fromtimestamp(int(timestamp)/1000)

                    if "text" in messaging_event["message"]: #key:text 
                        message_id = messaging_event["message"]["mid"]
                        sender_message = messaging_event["message"]["text"] # message text ="hello there"
                        config = CompanyConfig.query.filter_by(page_id=page_id).order_by(CompanyConfig.id.desc()).first()
                        if config:
                            conv=Conversation.query.filter_by(conv_id=sender_id).first()
                            if conv is None:
                                user = get_userinfo(sender_id, config.access_token)
                                user_name = user["first_name"] + " " +  user["last_name"]
                                new_conv = Conversation(name=user_name, conv_id = sender_id, page_id = page_id, type="fb", company_id= config.company_id)
                                db.session.add(new_conv)
                                db.session.commit()

                                member = Member(name=user_name, mobile_phone = sender_id, Conversation_id=new_conv.id)
                                db.session.add(member)
                                logging.info("****** member mjson ******")
                                logging.info(member)
                                member = Member(name="Business", mobile_phone = "Business", Conversation_id=new_conv.id)
                                db.session.add(member)
                                logging.info("****** member2 mjson ******")
                                logging.info(member)
                                db.session.commit()
                                logging.info("****** commit mjson ******")
                                logging.info(member)

                                message = Message(message_id = message_id, message_type="text",sender=sender_id, sender_message=sender_message,timestamp=datetime_obj, Conversation_id=new_conv.id, Member_id=member.id)
                                db.session.add(message)
                                db.session.commit()
                                logging.info("****** message mjson ******")
                                logging.info(member)
                                response = {
                                    'recipient': {'id': sender_id},
                                    "messaging_type": "RESPONSE",
                                    "message":{
                                        "text": fb_handle_message(sender_id, sender_message)
                                    }
                                }
                                logging.info("****** access token ******")
                                logging.info(config.access_tooken)
                                r = requests.post('https://graph.facebook.com/v16.0/'+ page_id +'/messages/?access_token=' + config.access_token, json=response)
                                data1 = json.loads(r.text)
                                logging.info("****** message sent mjson ******")
                                logging.info(data1)
                            else:
                                member = Member.query.filter(and_(Member.mobile_phone == sender_id, Member.Conversation_id==conv.id)).first()
                                if member:
                                    message = Message(message_id = message_id, message_type="text",sender=sender_id, sender_message=sender_message,timestamp=datetime_obj, Conversation_id=conv.id, Member_id=member.id)
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
                                        r = requests.post('https://graph.facebook.com/v16.0/'+ page_id +'/messages/?access_token=' + config.access_token, json=response)

        return Response(response="EVENT RECEIVED",status=200)
    except Exception as e:
        logging.error(str(e))
        return Response(response=str(e),status=500)

def fb_handle_message(user_id, user_message):
    # DO SOMETHING with the user_message ... ¯\_(ツ)_/¯
    return "Hello, how can I help you?"

# inatagram messenger webhook
@chat.route('/instagram/webhook', methods=['GET'])
def insta_webhook_verify():
    if request.args.get('hub.verify_token') == verify_token:
        return request.args.get('hub.challenge')
    return verify_token

@chat.route('/instagram/webhook', methods=['POST'])
def insta_webhook_action():
    try:
        mjson = request.get_json()
        logging.info("****** insta mjson ******")
        logging.info(mjson)
        logging.info("****** end insta mjson ******")
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
            r = requests.post('https://graph.facebook.com/v16.0/me/messages/?access_token=' + insta_access_token, json=response)
        return Response(response="EVENT RECEIVED",status=200)
    except Exception as e:
        logging.error(str(e))
        return Response(response=str(e),status=500)

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
    # try:

    # except Exception as e:
    #     logging.error(str(e))
    #     return Response(response=str(e),status=500)

    mjson = request.get_json()
    logging.error("****** wp mjson ******")
    logging.error(mjson)
    logging.error("****** end wp mjson ******")
    if is_message_notification(mjson):

        for entry in mjson["entry"]:
            for changes in entry["changes"]:
                name = "user"
                for contacts in changes["value"]["contacts"]:
                    name = contacts["profile"]["name"]
                conv_id = changes["value"]["metadata"]["phone_number_id"]
                for messages in changes["value"]["messages"]:
                    message_id = messages["id"]
                    timestamp = messages["timestamp"]
                    logging.error("****** after timestamp mjson ******")
                    logging.error(messages)
                    message_type = messages["type"]
                    sender = messages["from"]
                    sender_message = messages["text"]["body"]
                    datetime_obj = datetime.fromtimestamp(int(timestamp))

                    config = CompanyConfig.query.filter_by(phone_id=conv_id).order_by(CompanyConfig.id.desc()).first()
                    if config:
                        conv=Conversation.query.filter_by(conv_id=conv_id).first()
                        if conv is None:
                            new_conv = Conversation(name=name, conv_id = conv_id, page_id=conv_id, type="wp", company_id = config.company_id)
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
                            response = requests.post('https://graph.facebook.com/v16.0/'+ config.phone_id +'/messages?access_token=' + config.access_token, json=json_data)
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
                                response = requests.post('https://graph.facebook.com/v16.0/'+ config.phone_id +'/messages?access_token=' + config.access_token, json=json_data)

    return Response(response="EVENT RECEIVED",status=200)


@chat.route('/conversations/<int:userId>', methods=['GET'])
def conversations(userId):
    try:
        result = []
        user = User.query.get(userId)
        conversations = Conversation.query.filter_by(company_id=user.company_id)
        for con in conversations:
            members = []
            for mem in con.members:
                new_mem ={
                    'id': mem.id,
                    'name': mem.name,
                    'mobile_phone': mem.mobile_phone,
                    'Conversation_id': mem.Conversation_id
                }
                members.append(new_mem)

            new_obj = {
                'id':con.id,
                'name': con.name,
                'conv_id': con.conv_id,
                'type': con.type,
                'date_created': con.date_created,
                'page_id': con.page_id,
                'company_id': con.company_id,
                'members': members
            }

            result.append(new_obj)
        return jsonify(result)
    except Exception as e:
        logging.error(str(e))
        return 'Error: {}'.format(str(e)), 500

@chat.route('/messages/<int:conversationId>', methods=['GET'])
def messages(conversationId):
    try:
        result = []
        messages = Message.query.filter_by(Conversation_id=conversationId).all()
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
    except Exception as e:
        logging.error(str(e))
        return 'Error: {}'.format(str(e)), 500

@chat.route('/recentmessages/<int:conversationId>', methods=['GET'])
def recentmessages(conversationId):
    try:
        result = []
        messages = Message.query.filter_by(Conversation_id=conversationId).order_by(Message.id.desc()).limit(5).all()
        if messages:
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
        resp = make_response(jsonify(result))
        resp.status_code = 200
        return resp
    except Exception as e:
        logging.error(str(e))
        return 'Error: {}'.format(str(e)), 500

@chat.route('/sendmessage', methods=['POST'])
def sendmessage():
    try:
        data = request.get_json()
        type = data['type']
        conversationId = data['conversationId']
        page_id = data['pageId']
        memberId = data['memberId']
        message = data['message']
        recipient = data['recipient']
        if type == "wp":
            msg = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message
                }
            }
            timestamp = datetime.utcnow()
            config = CompanyConfig.query.filter_by(phone_id=page_id).order_by(CompanyConfig.id.desc()).first()
            response = requests.post('https://graph.facebook.com/v16.0/' + config.phone_id + '/messages?access_token=' + config.access_token, json=msg)
            if response.status_code == 200:
                data = json.loads(response.text)
                message_id = data["messages"][0]["id"]
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
        elif type == "fb":
            msg = {
                'recipient': {'id': recipient},
                "messaging_type": "RESPONSE",
                "message":{
                    "text": message
                }
            }
            logging.info(msg)
            timestamp = datetime.utcnow()
            config = CompanyConfig.query.filter_by(page_id=page_id).order_by(CompanyConfig.id.desc()).first()
            response = requests.post('https://graph.facebook.com/v16.0/'+ config.page_id +'/messages/?access_token=' + config.access_token, json=msg)
            if response.status_code == 200:
                data = json.loads(response.text)
                message_id = data["message_id"]
                messageObj = Message(message_id = message_id, message_type="text", sender="Business", sender_message=message, timestamp=timestamp, Conversation_id=conversationId, Member_id=memberId)
                db.session.add(messageObj)
                db.session.commit()
                new_obj = {
                    'id': messageObj.id,
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
    except Exception as e:
        logging.error(str(e))
        return 'Error: {}'.format(str(e)), 500


@chat.route('/chatapp', methods=['GET'])
def chatapp():
    return render_template('chatapp.html', user=current_user)


def wp_handle_message(user_id, user_message):
    return "Hello "+user_id+" ! You just sent me : " + user_message
