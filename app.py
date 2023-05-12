from website import create_app, socketio
from flask_mail import Mail, Message
from flask_googlemaps import GoogleMaps, Map, icons
from flask import render_template
from flask_login import login_user, login_required, logout_user, current_user
import os
from flask_cors import CORS

app = create_app()
CORS(app)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "sylvesterchima11@gmail.com"
app.config['MAIL_PASSWORD'] = "cgpfztdefimakjct"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
GoogleMaps(app, key="AIzaSyD0yxVcc3_gCrJRaW-GbiE7FDVxJ_H4MkU")



@app.route('/sendemail')
def sendemail():
    html = r'''
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Invite</title>
            </head>
            <body>
                <p> Hi [[0]]!</p>
                <p>You've been invited to join [[1]]. To verify your account, simply click on the button below or copy this link <a href="[[2]]">[[2]]</a></p>
                <a href="[[2]]" style="display:block; background-color:cornflowerblue; color: white; padding: 10px;">Click here</a>
                <p>Hope you will find [[1]] useful!</p>
                <p>
                    Best <br>
                    The [[1]] team
                </p>

            </body>
            </html>
        '''
    msg = Message('Trolog Invite', sender = 'sylvesterchima11@gmail.com')

    #if they are more than 1 recipient then loop through them and add the email like this
    msg.recipients.append('sylvesterchima11@outlook.com')

    #use msg.html instaed of msg.body then replace your placeholder in your template with value you want
    msg.html = html.replace('[[0]]','Chima').replace('[[1]]','Trolog').replace('[[2]]','http://127.0.0.1:5000/')
    mail.send(msg)
    return "sent"

@app.route("/map")
def map_created_in_view():

    gmap = Map(
        identifier="gmap",
        varname="gmap",
        lat=37.4419,
        lng=-122.1419,
        markers={
            icons.dots.green: [(37.4419, -122.1419), (37.4500, -122.1350)],
            icons.dots.blue: [(37.4300, -122.1400, "Hello World")],
        },
        style="height:400px;width:600px;margin:0;",
    )

    return render_template("mysample.html", gmap=gmap)


if __name__=='__main__':
    #wsgi.server(eventlet.listen(("127.0.0.1", 5000)), app)
    #app.run(host="0.0.0.0", port=5000, debug=True)#os.environ.get('DEBUG') == '1')
    socketio.run(app)












