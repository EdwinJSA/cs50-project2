import os
from collections import deque
from flask import Flask, render_template, session, request, redirect
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from helpers import login_required
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = "hello"
socketio = SocketIO(app)

channelsCreated = []
usersLogged = []
channelsMessages = dict()

@app.route("/")
@login_required
def index():
    return render_template("index.html", channels=channelsCreated)

@app.route("/signin", methods=['GET','POST'])
def signin():
    session.clear()
    username = request.form.get("username")
    if request.method == "POST":
        if len(username) < 1 or username == '':
            return render_template("error.html", message="Escribe un Apodo (Nickname)")
        if username in usersLogged:
            return render_template("error.html", message="Ya existe!!!")                   
        usersLogged.append(username)
        session['username'] = username
        session.permanent = True

        return redirect("/")
    else:
        return render_template("signin.html")

@app.route("/logout", methods=['GET'])
def logout():
    try:
        usersLogged.remove(session['username'])
    except ValueError:
        pass
    session.clear()
    return redirect("/")

@app.route("/create", methods=['POST'])
def create():
    newChannel = request.form.get("channel")
    if newChannel in channelsCreated:
        return render_template("error.html", message="Ha ocurrido un error")

    try:
        channelsCreated.append(newChannel)
        channelsMessages[newChannel] = deque()
        return redirect("/channels/" + newChannel)
    except:
        return render_template("error.html", message="Ha ocurrido")

@app.route("/channels/<channel>", methods=['GET','POST'])
@login_required
def enter_channel(channel):
    session['current_channel'] = channel

    if request.method == "POST":
        return redirect("/")
    else:
        print(channelsMessages.keys())
        return render_template("channel.html", channels= channelsCreated, messages=channelsMessages[channel])

@socketio.on("joined", namespace='/')
def joined():
    room = session.get('current_channel')
    join_room(room)
    emit('status', {
        'userJoined': session.get('username'),
        'channel': room,
        'msg': session.get('username') + ' entró al canal'}, 
        room=room)

@socketio.on("left", namespace='/')
def left():
    room = session.get('current_channel')
    leave_room(room)
    emit('status', {
        'msg': session.get('username') + ' has left the channel'}, 
        room=room)

@socketio.on('send message')
def send_msg(msg, timestamp):
    room = session.get('current_channel')
    if len(channelsMessages[room]) > 100:
        channelsMessages[room].popleft()

    channelsMessages[room].append([timestamp, session.get('username'), msg])
    emit('announce message', {
        'user': session.get('username'),
        'timestamp': timestamp,
        'msg': msg}, 
        room=room)