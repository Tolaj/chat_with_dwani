# let's import the flask
from flask import Flask, render_template, request, redirect, url_for
import os # importing operating system module
from config import get_database
import json
app = Flask(__name__)
# to stop caching static file
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

db = get_database()
users_collection = db['users']
chats_collection = db['chats']


@app.route('/') # this decorator create the home route
def home ():
    return render_template('index.html')

@app.route('/joinChat', methods= ['GET','POST'])
def joinChat(): 
    if request.method =='POST':
        username = request.form['userName']
        password = request.form['password']
        user = {
                'username': username,
                'password': password
            }
        existingUser = users_collection.find_one(user)
    
        if existingUser and existingUser['password'] == password:
            
            chatList = get_chat()
            myChatList = [item for item in chatList if item['username'] == username]
            strangerChatList = [item for item in chatList if item['username'] != username]
            return render_template('chat.html',username=username, myChatList=myChatList,strangerChatList=strangerChatList)
        else:
            return render_template('index.html', alertMsg = 'user does not exist with this username or incorrect password')



@app.route('/createUser', methods= ['GET','POST'])
def user(): 
    if request.method =='POST':
        username = request.form['userName']
        password = request.form['password']

        userQuery = create_user(username,password)
        
        if userQuery == 'USER_EXIST':
            return render_template('index.html', alertMsg = 'user already exist with this username!')
        else:
            return render_template('index.html', alertMsg = 'user created successfully!')


@app.route('/createChat', methods= ['GET','POST'])
def chat(): 
    if request.method =='POST':
        chat = request.form['chat']
        username = request.form['userName']

        create_chat(username,chat)
        
        chatList = get_chat()
        
        myChatList = [item for item in chatList if item['username'] == username]
        strangerChatList = [item for item in chatList if item['username'] != username]

                
        return render_template('chat.html',username=username, myChatList=myChatList,strangerChatList=strangerChatList)   


# User model functions
def create_user(username,password):
    user = {
        'username': username,
        'password': password
    }
    existingUser = users_collection.find_one(user)
    
    if existingUser :
        return 'USER_EXIST'
    else:
        result = users_collection.insert_one(user)
    return result.inserted_id  

# chat model functions
def create_chat(username,chat):
    chat = {
        'username': username,
        'chat':chat
    }
    result = chats_collection.insert_one(chat)
    return result.inserted_id  

def get_chat():
    chats = chats_collection.find()
    return list(chats)

if __name__ == '__main__':
    # for deployment
    # to make it work for both production and development
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)