from flask import Blueprint,redirect,url_for,render_template,session,request,flash,current_app,jsonify,Response,make_response
from .models import User, Conversation, Member, Message, Company, CompanyConfig
from datetime import datetime
import nanoid
import requests
import os.path
import os
from flask_login import login_user, login_required, logout_user, current_user
import json
from dotenv import load_dotenv
import logging
from sqlalchemy import and_, or_
from werkzeug.utils import secure_filename
from . import db
from flask_socketio import emit
from . import socketio


load_dotenv()
chat = Blueprint('chat', __name__,)
verify_token = os.getenv('VERIFY_TOKEN')
insta_access_token = os.getenv('INSTA_ACCESS_TOKEN')
baseUrl=os.getenv('BASEURL')

def is_message_notification(data):
    try:
        if data["object"]=="page":  #if true hngeeb entry [list]
            for entry in data["entry"]:
                for messaging_event in entry["messaging"]: #3shan ad5ol 3la list 
                    #sender_id = messaging_event["sender"]["id"]
                    #recipient_id = messaging_event["recipient"]["id"] #bgeb mn eldict elrecipient key
                    if messaging_event.get("message"):
                        return True
                    else:
                        return False
        elif data["object"]=="whatsapp_business_account":
            for entry in data["entry"]:
                for changes_event in entry["changes"]: #3shan ad5ol 3la list 
                    if changes_event["field"] == "messages":
                        if changes_event["value"].get("messages"):
                            return True
                        else:
                            return False
                    else:
                        return False
        elif data["object"]=="instagram":
            for entry in data["entry"]:
                for messaging_event in entry["messaging"]: #3shan ad5ol 3la list
                    if messaging_event.get("message"):
                        return True
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
    # db.session.query(CompanyConfig).delete()
    # db.session.commit()
    # db.session.query(User).delete()
    # db.session.commit()
    # db.session.query(Company).delete()
    # db.session.commit()
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
                    message_id = messaging_event["message"]["mid"]
                    tagMsg = {
                        "recipient":{
                            "id":sender_id
                        },
                        "message":{
                            "attachment":{
                            "type":"template",
                            "payload":{
                                "template_type":"generic",
                                "elements":[
                                {
                                    "title":"Welcome!",
                                    "image_url":"https://fastly.picsum.photos/id/866/200/300.jpg?hmac=rcadCENKh4rD6MAp6V_ma-AyWv641M4iiOpe1RyFHeI",
                                    "subtitle":"We offers the best toolkits for medium and large organisations to monitor and improve employee and customer satisfaction.",
                                    "default_action": {
                                    "type": "web_url",
                                    "url": "https://troologdemo.azurewebsites.net/",
                                    "webview_height_ratio": "tall"
                                    },
                                    "buttons":[
                                    {
                                        "type":"web_url",
                                        "url":"https://troologdemo.azurewebsites.net/",
                                        "title":"View Website"
                                    }]
                                }]
                            }
                            }
                        }
                    }
                    sender_AttachmentUrl = None
                    sender_message = None
                    sender_messageType = "text"
                    if "text" in messaging_event["message"]: #key:text
                        sender_message = messaging_event["message"]["text"]
                    if "attachments" in messaging_event["message"]:
                        sender_AttachmentUrl = messaging_event["message"]["attachments"][0]["payload"]["url"]
                        sender_messageType = messaging_event["message"]["attachments"][0]["type"]
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
                            member = Member(name="Business", mobile_phone = "Business", Conversation_id=new_conv.id)
                            db.session.add(member)
                            db.session.commit()
                            message = Message(message_id = message_id, message_type=sender_messageType,sender=sender_id, sender_message=sender_message,timestamp=datetime_obj, Conversation_id=new_conv.id, Member_id=member.id,image_url=sender_AttachmentUrl)
                            db.session.add(message)
                            db.session.commit()
                            r = requests.post('https://graph.facebook.com/v16.0/'+ page_id +'/messages/?access_token=' + config.access_token, json=tagMsg)
                            data1 = json.loads(r.text)
                            logging.info("****** message sent mjson ******")
                            logging.info(data1)
                        else:
                            last_message = Message.query.filter(and_(Message.sender == sender_id, Message.Conversation_id==conv.id)).order_by(Message.id.desc()).first()
                            member = Member.query.filter(and_(Member.mobile_phone == sender_id, Member.Conversation_id==conv.id)).first()
                            if member:
                                message = Message(message_id = message_id, message_type=sender_messageType,sender=sender_id, sender_message=sender_message,timestamp=datetime_obj, Conversation_id=conv.id, Member_id=member.id,image_url=sender_AttachmentUrl)
                                db.session.add(message)
                                db.session.commit()

                            if last_message:
                                hour_difference = (datetime.utcnow() - last_message.timestamp).total_seconds() / 3600
                                if hour_difference >= 24:
                                    r = requests.post('https://graph.facebook.com/v16.0/'+ page_id +'/messages/?access_token=' + config.access_token, json=tagMsg)
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
    mode = request.args['hub.mode']
    token = request.args['hub.verify_token']
    challenge = request.args['hub.challenge']
    if mode and token:
      if mode == 'subscribe' and token == verify_token:
        print("subscribed")
        return challenge
      else:
        print("wrong token")
        return make_response('wrong token', 403)
    else:
      print("invalid params")
      return make_response('invalid params', 400)

@chat.route('/instagram/webhook', methods=['POST'])
def insta_webhook_action():
    try:
        mjson = request.get_json()
        logging.info("****** insta mjson ******")
        logging.info(mjson)
        logging.info("****** end insta mjson ******")
        if is_message_notification(mjson):
            logging.info("****** valid mjson ******")
            for entry in mjson["entry"]:
                logging.info("****** Entry mjson ******")
                page_id = entry["id"]
                for messaging_event in entry["messaging"]:
                    logging.info("****** messaging mjson ******")
                    sender_id = messaging_event["sender"]["id"]
                    recipient_id = messaging_event["recipient"]["id"] #bgeb mn eldict elrecipient key
                    timestamp = messaging_event["timestamp"]
                    datetime_obj = datetime.fromtimestamp(int(timestamp)/1000)
                    message_id = messaging_event["message"]["mid"]
                    logging.info("****** tagMsg mjson ******")
                    tagMsg = {
                        "recipient":{
                            "id":sender_id
                        },
                        "message":{
                            "attachment":{
                            "type":"template",
                            "payload":{
                                "template_type":"generic",
                                "elements":[
                                {
                                    "title":"Welcome!",
                                    "image_url":"https://fastly.picsum.photos/id/866/200/300.jpg?hmac=rcadCENKh4rD6MAp6V_ma-AyWv641M4iiOpe1RyFHeI",
                                    "subtitle":"We offers the best toolkits for medium and large organisations to monitor and improve employee and customer satisfaction.",
                                    "default_action": {
                                    "type": "web_url",
                                    "url": "https://troolog.onrender.com/",
                                    "webview_height_ratio": "tall"
                                    },
                                    "buttons":[
                                    {
                                        "type":"web_url",
                                        "url":"https://troolog.onrender.com/",
                                        "title":"View Website"
                                    }]
                                }]
                            }
                            }
                        }
                    }
                    sender_AttachmentUrl = None
                    sender_message = None
                    sender_messageType = "text"
                    if "text" in messaging_event["message"]: #key:text
                        sender_message = messaging_event["message"]["text"]
                    if "attachments" in messaging_event["message"]:
                        sender_AttachmentUrl = messaging_event["message"]["attachments"][0]["payload"]["url"]
                        sender_messageType = messaging_event["message"]["attachments"][0]["type"]
                    logging.info("****** before config mjson ******")
                    config = CompanyConfig.query.filter_by(page_id=page_id).order_by(CompanyConfig.id.desc()).first()
                    if config:
                        logging.info("****** config mjson ******")
                        conv=Conversation.query.filter_by(conv_id=sender_id).first()
                        if conv is None:
                            logging.info("****** conv mjson ******")
                            user = get_userinfo(sender_id, config.access_token)
                            user_name = user["first_name"] + " " +  user["last_name"]
                            new_conv = Conversation(name=user_name, conv_id = sender_id, page_id = page_id, type="insta", company_id= config.company_id)
                            db.session.add(new_conv)
                            db.session.commit()

                            member = Member(name=user_name, mobile_phone = sender_id, Conversation_id=new_conv.id)
                            db.session.add(member)
                            member = Member(name="Business", mobile_phone = "Business", Conversation_id=new_conv.id)
                            db.session.add(member)
                            db.session.commit()
                            message = Message(message_id = message_id, message_type=sender_messageType,sender=sender_id, sender_message=sender_message,timestamp=datetime_obj, Conversation_id=new_conv.id, Member_id=member.id,image_url=sender_AttachmentUrl)
                            db.session.add(message)
                            db.session.commit()
                            r = requests.post('https://graph.facebook.com/v16.0/'+ page_id +'/messages/?access_token=' + config.access_token, json=tagMsg)
                            data1 = json.loads(r.text)
                            logging.info("****** message sent mjson ******")
                            logging.info(data1)
                        else:
                            logging.info("****** conv exist mjson ******")
                            last_message = Message.query.filter(and_(Message.sender == sender_id, Message.Conversation_id==conv.id)).order_by(Message.id.desc()).first()
                            member = Member.query.filter(and_(Member.mobile_phone == sender_id, Member.Conversation_id==conv.id)).first()
                            if member:
                                logging.info("****** member mjson ******")
                                message = Message(message_id = message_id, message_type=sender_messageType,sender=sender_id, sender_message=sender_message,timestamp=datetime_obj, Conversation_id=conv.id, Member_id=member.id,image_url=sender_AttachmentUrl)
                                db.session.add(message)
                                db.session.commit()

                            if last_message:
                                hour_difference = (datetime.utcnow() - last_message.timestamp).total_seconds() / 3600
                                if hour_difference >= 24:
                                    r = requests.post('https://graph.facebook.com/v16.0/'+ page_id +'/messages/?access_token=' + config.access_token, json=tagMsg)
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
    try:
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
                    phone_id = changes["value"]["metadata"]["phone_number_id"]
                    conv_id = contacts["wa_id"]
                    for messages in changes["value"]["messages"]:
                        message_id = messages["id"]
                        timestamp = messages["timestamp"]
                        logging.error("****** after timestamp mjson ******")
                        logging.error(messages)
                        message_type = messages["type"]
                        sender = messages["from"]

                        sender_media_id = None
                        sender_message = None
                        sender_media_url = None
                        if "text" in messages: #key:text
                            print("****text******")
                            sender_message = messages["text"]["body"]
                        if "image" in messages:
                            print("****image******")
                            sender_media_id = messages["image"]["id"]
                            if "caption" in messages["image"]:
                                sender_message = messages["image"]["caption"]

                        datetime_obj = datetime.fromtimestamp(int(timestamp))

                        templateMsg = {
                            "messaging_product": "whatsapp","to": sender,"type": "template",
                            "template": {
                                "name": "hello_world",
                                "language": {
                                    "code": "en_US"
                                }
                            }
                        }

                        config = CompanyConfig.query.filter_by(phone_id=phone_id).order_by(CompanyConfig.id.desc()).first()
                        if config:
                            if sender_media_id:
                                headers = {
                                    "Authorization": "Bearer " + config.access_token
                                }
                                logging.error("****** image info ******")
                                print(config.access_token)
                                logging.error(sender_media_id)
                                imgResponse = requests.get('https://graph.facebook.com/v16.0/'+ sender_media_id + '/', headers=headers)
                                ndata = json.loads(imgResponse.text)
                                logging.error(ndata)
                                if imgResponse.status_code == 200:
                                    img_url = ndata["url"]
                                    logging.error(img_url)
                                    downlodResponse = requests.get(img_url, headers=headers)
                                    file_name = 'wp_' + nanoid.generate() + '_' + conv_id + '_app.jpg'
                                    f_name=os.path.join(current_app.config['UPLOAD_FOLDER'], file_name)
                                    with open(f_name, "wb") as file:
                                        file.write(downlodResponse.content)
                                    sender_media_url = baseUrl + url_for('static', filename='uploads/' + file_name)

                            conv=Conversation.query.filter_by(conv_id=conv_id).first()
                            if conv is None:
                                new_conv = Conversation(name=name, conv_id = conv_id, page_id=phone_id, type="wp", company_id = config.company_id)
                                db.session.add(new_conv)
                                db.session.commit()

                                member = Member(name=name, mobile_phone = sender, Conversation_id=new_conv.id)
                                db.session.add(member)
                                member = Member(name="Business", mobile_phone = "Business", Conversation_id=new_conv.id)
                                db.session.add(member)
                                db.session.commit()

                                message = Message(message_id = message_id, message_type=message_type,sender=sender, sender_message=sender_message,timestamp=datetime_obj, Conversation_id=new_conv.id, Member_id=member.id,image_url=sender_media_url)
                                db.session.add(message)
                                db.session.commit()
                                response = requests.post('https://graph.facebook.com/v16.0/'+ config.phone_id +'/messages?access_token=' + config.access_token, json=templateMsg)
                            else:
                                last_message = Message.query.filter(and_(Message.sender == sender, Message.Conversation_id==conv.id)).order_by(Message.id.desc()).first()
                                member = Member.query.filter(and_(Member.mobile_phone == sender, Member.Conversation_id==conv.id)).first()
                                if member:
                                    message = Message(message_id = message_id, message_type=message_type,sender=sender, sender_message=sender_message,timestamp=datetime_obj, Conversation_id=conv.id, Member_id=member.id,image_url=sender_media_url)
                                    db.session.add(message)
                                    db.session.commit()

                                hour_difference = (datetime.utcnow() - last_message.timestamp).total_seconds() / 3600
                                if hour_difference >= 24:
                                    response = requests.post('https://graph.facebook.com/v16.0/'+ config.phone_id +'/messages?access_token=' + config.access_token, json=templateMsg)

        return Response(response="EVENT RECEIVED",status=200)
    except Exception as e:
        logging.error(str(e))
        return 'Error: {}'.format(str(e)), 500

@chat.route('/api_attachement/<string:page_id>', methods=['POST'])
def api_attachement(page_id):
    file = request.files['image']
    nanoid.generate()
    if file.filename != '':
        filename = secure_filename(file.filename)
        f_name=nanoid.generate() + '_' + page_id + '_' + filename
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], f_name))
        return baseUrl + url_for('static', filename='uploads/') + f_name, 200
    else:
        return 'failed', 400
    # data = {
    #     'message': '{"attachment":{"type":"image", "payload":{"is_reusable":true}}}'
    # }
    # files = {
    #     'filedata': (file.filename, file.stream, file.content_type)
    # }
    # config = CompanyConfig.query.filter_by(page_id=page_id).order_by(CompanyConfig.id.desc()).first()
    # response = requests.post('https://graph.facebook.com/v16.0/me/message_attachments?access_token=' + config.access_token, data=data, files=files)
    # resp = json.loads(response.text)
    # if response.status_code == 200:
    #     attachment_id = resp["attachment_id"]
    #     return attachment_id
    # else:
    #     return 'Image upload failed', response.status_code


@chat.route('/conversations/<int:userId>', methods=['GET'])
@login_required
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
                'image_url': con.image_url,
                'timestamp': con.timestamp,
                'Conversation_id': con.Conversation_id,
                'Member_id': con.Member_id
            }
            result.append(new_obj)
        return jsonify(result)
    except Exception as e:
        logging.error(str(e))
        return 'Error: {}'.format(str(e)), 500

@chat.route('/webmessages/<string:chatsession>', methods=['GET'])
def web_messages(chatsession):
    try:
        result = []
        conv = Conversation.query.filter_by(conv_id = chatsession).first()
        messages = Message.query.filter_by(Conversation_id=conv.id).all()
        for con in messages:
            new_obj = {
                'id':con.id,
                'message_id': con.message_id,
                'message_type': con.message_type,
                'sender': con.sender,
                'sender_message': con.sender_message,
                'image_url': con.image_url,
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
                    'image_url': con.image_url,
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
        fileUrl = data['fileUrl']
        message_type="text"
        if type == "wp":
            msg = {}
            if fileUrl:
                msg = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": recipient,
                    "type": "image",
                    "image": {
                        "link" : fileUrl
                    }
                }
                message_type = "image"
            else:
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
            wpdata = json.loads(response.text)
            logging.info("****** whatsapp send response mjson ******")
            logging.info(wpdata)
            if response.status_code == 200:
                data = json.loads(response.text)
                message_id = data["messages"][0]["id"]
                messageObj = Message(message_id = message_id, message_type=message_type,sender="Business", sender_message=message,timestamp=timestamp, Conversation_id=conversationId, Member_id=memberId,image_url=fileUrl)
                db.session.add(messageObj)
                db.session.commit()
                new_obj = {
                    'id':messageObj.id,
                    'message_id': message_id,
                    'message_type': message_type,
                    'sender': "Business",
                    'sender_message': message,
                    'image_url': fileUrl,
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
            msg = {}
            if fileUrl:
                msg = {
                    "recipient": {"id": recipient},
                    "messaging_type": "RESPONSE",
                    "message":{
                        "attachment":{
                            "type":"image",
                            "payload":{
                                "url":fileUrl,
                                "is_reusable":True
                            }
                        }
                    }
                }
                message_type = "image"
            else:
                msg = {
                    "recipient": {"id": recipient},
                    "messaging_type": "RESPONSE",
                    "message":{
                        "text": message
                    }
                }
            logging.info(msg)
            timestamp = datetime.utcnow()
            config = CompanyConfig.query.filter_by(page_id=page_id).order_by(CompanyConfig.id.desc()).first()
            logging.info("****** Config mjson ******")
            logging.info(config.page_id)
            logging.info(config.access_token)
            response = requests.post('https://graph.facebook.com/v16.0/'+ config.page_id +'/messages/?access_token=' + config.access_token, json=msg)
            data = json.loads(response.text)
            logging.info("****** response mjson ******")
            logging.info(data)
            print(data)
            if response.status_code == 200:
                message_id = data["message_id"]
                messageObj = Message(message_id = message_id, message_type=message_type, sender="Business", sender_message=message, timestamp=timestamp, Conversation_id=conversationId, Member_id=memberId,image_url=fileUrl)
                db.session.add(messageObj)
                db.session.commit()
                new_obj = {
                    'id': messageObj.id,
                    'message_id': message_id,
                    'message_type': message_type,
                    'sender': "Business",
                    'sender_message': message,
                    'image_url': fileUrl,
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
        elif type == "web":
            datetime_obj = datetime.now()
            company = Company.query.filter_by(id = current_user.company_id).first()
            media_url = None
            if fileUrl:
                media_url = fileUrl
                message_type = "image"
            sentMessage = Message(message_id = nanoid.generate(), message_type=message_type,sender="Business", sender_message=message,timestamp=datetime_obj, Conversation_id=conversationId, Member_id=memberId,image_url=media_url)
            db.session.add(sentMessage)
            db.session.commit()

            new_obj = {
                'id': sentMessage.id,
                'message_id': sentMessage.message_id,
                'message_type': message_type,
                'sender': "Business",
                'sender_message': sentMessage.sender_message,
                'image_url': fileUrl,
                'timestamp': sentMessage.timestamp,
                'Conversation_id': sentMessage.Conversation_id,
                'Member_id': sentMessage.Member_id
            }
            msg_obj = {
                'message_id':sentMessage.message_id,
                'name': current_user.last_name + ' ' + current_user.first_name,
                'email': current_user.email,
                'org_id': company.id,
                'org_name': company.name,
                'message_type': sentMessage.message_type,
                'sender': "Business",
                'message': sentMessage.sender_message,
                'timestamp': sentMessage.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'Conversation_id': sentMessage.Conversation_id,
                'Member_id': sentMessage.Member_id,
                'chat_session': page_id,
                'image_url': fileUrl
            }
            socketio.emit("chat", msg_obj)
            resp = make_response(new_obj)
            resp.status_code = 200
            return resp
        elif type == "insta":
            msg = {}
            if fileUrl:
                msg = {
                    "recipient": {"id": recipient},
                    "messaging_type": "RESPONSE",
                    "message":{
                        "attachment":{
                            "type":"image",
                            "payload":{
                                "url":fileUrl,
                                "is_reusable":True
                            }
                        }
                    }
                }
                message_type = "image"
            else:
                msg = {
                    "recipient": {"id": recipient},
                    "messaging_type": "RESPONSE",
                    "message":{
                        "text": message
                    }
                }
            logging.info(msg)
            timestamp = datetime.utcnow()
            config = CompanyConfig.query.filter_by(page_id=page_id).order_by(CompanyConfig.id.desc()).first()
            logging.info("****** Config mjson ******")
            logging.info(config.page_id)
            logging.info(config.access_token)
            response = requests.post('https://graph.facebook.com/v16.0/'+ config.page_id +'/messages/?access_token=' + config.access_token, json=msg)
            data = json.loads(response.text)
            logging.info("****** response mjson ******")
            logging.info(data)
            print(data)
            if response.status_code == 200:
                message_id = data["message_id"]
                messageObj = Message(message_id = message_id, message_type=message_type, sender="Business", sender_message=message, timestamp=timestamp, Conversation_id=conversationId, Member_id=memberId,image_url=fileUrl)
                db.session.add(messageObj)
                db.session.commit()
                new_obj = {
                    'id': messageObj.id,
                    'message_id': message_id,
                    'message_type': message_type,
                    'sender': "Business",
                    'sender_message': message,
                    'image_url': fileUrl,
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


@chat.route('/sendtagmessage', methods=['POST'])
def sendtagmessage():
    try:
        data = request.get_json()
        type = data['type']
        conversationId = data['conversationId']
        page_id = data['pageId']
        memberId = data['memberId']
        message = "Tag Message"
        recipient = data['recipient']
        if type == "wp":
            msg = {
                "messaging_product": "whatsapp","to": recipient,"type": "template",
                "template": {
                    "name": "hello_world",
                    "language": {
                        "code": "en_US"
                    }
                }
            }
            timestamp = datetime.utcnow()
            config = CompanyConfig.query.filter_by(phone_id=page_id).order_by(CompanyConfig.id.desc()).first()
            response = requests.post('https://graph.facebook.com/v16.0/' + config.phone_id + '/messages?access_token=' + config.access_token, json=msg)
            if response.status_code == 200:
                data = json.loads(response.text)
                message_id = data["messages"][0]["id"]
                messageObj = Message(message_id = message_id, message_type="tag",sender="Business", sender_message=message,timestamp=timestamp, Conversation_id=conversationId, Member_id=memberId)
                db.session.add(messageObj)
                db.session.commit()
                new_obj = {
                    'id':messageObj.id,
                    'message_id': message_id,
                    'message_type': "tag",
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
                "recipient":{
                    "id":recipient
                },
                "message":{
                    "attachment":{
                        "type":"template",
                        "payload":{
                            "template_type":"generic",
                            "elements":[
                            {
                                "title":"Welcome!",
                                "image_url":"https://fastly.picsum.photos/id/866/200/300.jpg?hmac=rcadCENKh4rD6MAp6V_ma-AyWv641M4iiOpe1RyFHeI",
                                "subtitle":"We offers the best toolkits for medium and large organisations to monitor and improve employee and customer satisfaction.",
                                "default_action": {
                                "type": "web_url",
                                "url": "https://troologdemo.azurewebsites.net/",
                                "webview_height_ratio": "tall"
                                },
                                "buttons":[
                                {
                                    "type":"web_url",
                                    "url":"https://troologdemo.azurewebsites.net/",
                                    "title":"View Website"
                                }]
                            }]
                        }
                    }
                }
            }
            logging.info(msg)
            timestamp = datetime.utcnow()
            config = CompanyConfig.query.filter_by(page_id=page_id).order_by(CompanyConfig.id.desc()).first()
            logging.info("****** Config mjson ******")
            logging.info(config.page_id)
            logging.info(config.access_token)
            response = requests.post('https://graph.facebook.com/v16.0/'+ config.page_id +'/messages/?access_token=' + config.access_token, json=msg)
            data = json.loads(response.text)
            logging.info("****** response mjson ******")
            logging.info(data)
            if response.status_code == 200:
                message_id = data["message_id"]
                messageObj = Message(message_id = message_id, message_type="tag", sender="Business", sender_message=message, timestamp=timestamp, Conversation_id=conversationId, Member_id=memberId)
                db.session.add(messageObj)
                db.session.commit()
                new_obj = {
                    'id': messageObj.id,
                    'message_id': message_id,
                    'message_type': "tag",
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
@login_required
def chatapp():
    return render_template('chatapp.html', user=current_user,baseUrl=baseUrl)

@chat.route('/minichat/<int:org_id>', methods=['GET'])
def minichat(org_id):
    company = Company.query.filter_by(id = org_id).first()
    return render_template('minichat.html', user=current_user, org_name=company.name, org_id = company.id)


@socketio.on('connect')
def handle_connect():
    print("client connected")

@socketio.on("user_connected")
def handle_user_connected(data):
    name = data['name']
    email = data['email']
    chat_session = data['chat_session']
    org_id = data['org_id']
    org_name = data['org_name']
    fileUrl = data['file_url']
    print('*********** user is connected************')
    print(f"User joined! {chat_session}")
    conv = Conversation.query.filter_by(conv_id=chat_session).first()
    if conv is None:
        new_conv = Conversation(name= org_name + " (" + name + ")", conv_id = chat_session, page_id=chat_session, type="web", company_id = org_id)
        db.session.add(new_conv)
        db.session.commit()

        member = Member(name=name, mobile_phone = email, Conversation_id=new_conv.id)
        db.session.add(member)
        member = Member(name="Business", mobile_phone = "Business", Conversation_id=new_conv.id)
        db.session.add(member)
        db.session.commit()
        company = Company.query.filter_by(id = org_id).first()
        datetime_obj = datetime.now()

        message_type = "text"
        media_url = None
        if fileUrl:
            media_url = fileUrl
            message_type = "image"

        message = Message(message_id = nanoid.generate(), message_type=message_type,sender="Business", sender_message="Hello, How may i help you?",timestamp=datetime_obj, Conversation_id=new_conv.id, Member_id=member.id,image_url=media_url)
        db.session.add(message)
        db.session.commit()

        msg_obj = {
            'message_id':message.message_id,
            'name': company.name,
            'email': company.website,
            'org_id': org_id,
            'org_name': org_name,
            'message_type': message.message_type,
            'sender': "Business",
            'message': message.sender_message,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'Conversation_id': message.Conversation_id,
            'Member_id': message.Member_id,
            'chat_session': chat_session,
            'image_url': fileUrl
        }

        emit("chat", msg_obj, broadcast=True)

@socketio.on("new_message")
def handle_new_message(data):
    name = data['name']
    email = data['email']
    chat_session = data['chat_session']
    org_id = data['org_id']
    org_name = data['org_name']
    message = data['message']
    fileUrl = data['file_url']
    print(f"New message: {message}")
    conv=Conversation.query.filter_by(conv_id=chat_session).first()
    if conv is not None:
        datetime_obj = datetime.now()
        member = Member.query.filter(and_(Member.mobile_phone == email, Member.Conversation_id==conv.id)).first()
        if member is not None:
            message_type = "text"
            media_url = None
            if fileUrl:
                media_url = fileUrl
                message_type = "image"

            sentMessage = Message(message_id = nanoid.generate(), message_type=message_type,sender=email, sender_message=message,timestamp=datetime_obj, Conversation_id=conv.id, Member_id=member.id,image_url=media_url)
            db.session.add(sentMessage)
            db.session.commit()

            msg_obj = {
                'message_id':sentMessage.message_id,
                'name': name,
                'email': email,
                'org_id': org_id,
                'org_name': org_name,
                'message_type': sentMessage.message_type,
                'sender': email,
                'message': sentMessage.sender_message,
                'timestamp': sentMessage.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'Conversation_id': sentMessage.Conversation_id,
                'Member_id': sentMessage.Member_id,
                'chat_session': chat_session,
                'image_url': fileUrl
            }
            emit("chat", msg_obj, broadcast=True)






