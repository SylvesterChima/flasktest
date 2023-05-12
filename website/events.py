# from flask_socketio import emit
# from . import socketio
# from . import db


# @socketio.on('connect')
# def handle_connect():
#     print("client connected")

# @socketio.on("user_connected")
# def handle_user_connected(user):
#     # name = user['name']
#     # email = user['email']
#     # chat_id = user['chatsession']
#     print('*********** user is connected************')
#     #print(f"User  joined! {chat_id}")
#     # new_conv = Conversation(name=name, conv_id = chat_id, page_id=email, type="web", company_id = 1)
#     # mdb.session.add(new_conv)
#     # mdb.session.commit()

#     # member = Member(name=name, mobile_phone = email, Conversation_id=new_conv.id)
#     # mdb.session.add(member)
#     # member = Member(name="Business", mobile_phone = "Business", Conversation_id=new_conv.id)
#     # mdb.session.add(member)
#     # mdb.session.commit()

# @socketio.on("new_message")
# def handle_new_message(data):
#     emit("chat","hiiiii********")
#     name = data['name']
#     email = data['email']
#     chat_id = data['chatsession']
#     message = data['message']
#     print(f"New message: {message}")
#     # conv=Conversation.query.filter_by(conv_id=chat_id).first()
#     # datetime_obj = datetime.now()
#     # member = Member.query.filter(and_(Member.mobile_phone == email, Member.Conversation_id==conv.id)).first()
#     # message = Message(message_id = nanoid.generate(), message_type="text",sender=chat_id, sender_message=message,timestamp=datetime_obj, Conversation_id=conv.id, Member_id=member.id)
#     # mdb.session.add(message)
#     # mdb.session.commit()
#     #username = None
#     # for user in users:
#     #     if users[user] == request.sid:
#     #         username = user
#     emit("chat", {"message": message, "name": name}, broadcast=True)

