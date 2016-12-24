# -*- coding: utf-8 -*-
#!/usr/bin/env python

from flask import Flask, render_template, session, request, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import time
import loli_h

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secrtjyfyuiuguyyur67i8tgyet!'
socketio = SocketIO(app, async_mode=async_mode)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        n = request.form.get('username','')
        p = request.form.get('userpass','')
        if n and p:
            session["username"] = n
            session["userpass"] = p
        else:
            return redirect("/")
    else:
        pass
    username = session.get('username', '')
    userpass = session.get('userpass', '')
    if username and userpass:
        return render_template('signin.html')
    else:
        return redirect("/")

@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    username = session.get('username', "456@456.com")
    userpass = session.get('userpass', "123")
    s = loli_h.getSession()
    emit('iresponse',
         {'data': "获得 session", 'count': session['receive_count']})
    passkey, uaid, s = loli_h.getpasskeyuaid(s)
    emit('sresponse',
         {'data': "提取出key和uaid", 'count': session['receive_count']})
    passencrypted, newuaid = loli_h.getpenu(userpass, passkey, uaid)
    emit('sresponse',
         {'data': "密码加密成功", 'count': session['receive_count']})
    code, msg, s = loli_h.loginstatus(s, newuaid, username, passencrypted)
    if code == u"1":
    	emit('sresponse',
         {'data': "登录成功!", 'count': session['receive_count']})
    else:
    	emit('eresponse',
         {'data': "失败，密码错误", 'count': session['receive_count']})
        s.close()
        return
    s, uaid2 = loli_h.qiandaos1(s)
    emit('sresponse',
         {'data': "取出用户页uaid", 'count': session['receive_count']})
    code, msg = loli_h.qiandaos2(s, uaid2)
    if code == 1:
    	emit('sresponse',
         {'data': "签到成功"+msg, 'count': session['receive_count']})
    else:
    	emit('wresponse',
         {'data': "失败签到，可能你已经签到过了", 'count': session['receive_count']})
    


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, port=8000, debug=False)
