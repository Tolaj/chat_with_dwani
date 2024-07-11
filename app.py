# let's import the flask
from flask import Flask, render_template, request, redirect, url_for
import os # importing operating system module
from config import get_database
import json
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO,join_room, leave_room,emit,send



app = Flask(__name__)
# to stop caching static file
app.config['SECRET_KEY'] = 'secret!'
cors = CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app)

# database ----------------------------------------------------
db = get_database()

rooms_collection = db['rooms']


# routes ----------------------------------------------------
@app.route('/') # this decorator create the home route
def home ():
    rooms = [dict["roomID"] for dict in get_room()]
    return render_template('index.html',rooms=rooms)

@app.route('/joinRoom', methods= ['GET','POST'])
def joinRoom(): 
    if request.method =='POST':
        username = request.form['username']
        room = request.form['room']
        return render_template('chat.html',username=username, room=room)
        

# socket methods -----------------------------------------------------



@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    create_room(room)
    data['msg'] = username + ' has entered the room.'
    send(data, to=room)



@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)

    # rooms_collection.delete_many({})
    data['msg'] = username + ' has left the room.'
    send(data, to=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    print(socketio)
    send(data, to=room)


# user defined methods ----------------------------------------------------

def get_room():
    rooms = rooms_collection.find()
    return list(rooms)

def create_room(room_id):

    rooms = list(rooms_collection.find())

    
    existingRoom = rooms_collection.find_one({'roomID':room_id})

    if not existingRoom :
        rooms_collection.insert_one({'roomID':room_id})
    return rooms




# main method ----------------------------------------------------

if __name__ == '__main__':
    socketio.run(app)
    app.run(host='0.0.0.0', port=5000, debug=True)