import eventlet
eventlet.monkey_patch()

import os
os.environ['EVENTLET_NO_GREENDNS'] = 'yes'

from flask import Flask, request, jsonify, json
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId, Timestamp, json_util
from flask_socketio import SocketIO, send, emit
import random
import string
import json
import datetime


from Lobby import Lobby

# Fields for the Server
version = '0.001'
lobbies = []



# Web server stuff
app = Flask(__name__)
app.config['SECRET_KEY'] = 'onesouth'
socketio = SocketIO(app)
CORS(app)

# DB URL
DBURL = 'mongodb+srv://walkerreynolds16:onesouth@thelargecluster-ybjdm.mongodb.net/test?retryWrites=true'

def startServer():
    client = MongoClient(DBURL + ":27017")
    db = client.Clubin_tv

    collection = db['Lobbies']
    collection.delete_many({})

@app.route('/getVersion', methods=['GET'])
def getVersion():
    return json.dumps(version)

@app.route('/createLobby', methods=['POST'])
def createLobby():
    client = MongoClient(DBURL + ":27017")
    db = client.Clubin_tv

    collection = db['Lobbies']

    createdLobby = False
    randomCode = ''

    while(not createdLobby): # Loop creates a new lobby code and checks if its being used
        randomCode = ''
        for i in range(4):
            randomCode += random.choice(string.ascii_uppercase)
        
        playlist = collection.find_one({'lobbyCode': randomCode})

        # if lobby code isn't being used, break out of loop
        # else keep going
        if(playlist == None):
            # Code IS NOT in use
            createdLobby = True

    global lobbies

    newLobby = Lobby(randomCode)
    lobbies.append(newLobby)
    print(lobbies)

    res = collection.insert_one({'lobbyCode': randomCode, 'connectedUsers': 0, 'dateCreated': datetime.datetime.now()})
    # return JSONEncoder().encode(res.inserted_id)
    return randomCode

@app.route('/deleteLobby', methods=['POST'])
def deleteLobby():
    # delete lobby from lobbies list and DB entry
    # lobbyCode = request.json['lobbyCode']
    lobbyCode = request.json['lobbyCode']

    global lobbies

    # remove lobby from server array
    for lobby in lobbies:
        if(lobby.getLobbyCode() == lobbyCode):
            lobbies.remove(lobby)
            break
    
    client = MongoClient(DBURL + ":27017")
    db = client.Clubin_tv

    collection = db['Lobbies']

    res = collection.delete_one({'lobbyCode': lobbyCode})
    print(res.deleted_count)

    return JSONEncoder().encode(lobbies)
    
@app.route('/addVideo', methods=['POST'])
def addVideo():
    lobbyCode = request.json['lobbyCode']
    videoId = request.json['videoId']
    global lobbies

    for lobby in lobbies:
        if(lobby.getLobbyCode() == lobbyCode):
            lobby.addVideoToQueue(videoId)
            return JSONEncoder().encode(lobby.getVideoQueue())

    return "Didn't find lobby"

@app.route('/getNextVideo', methods=['POST',])
def getNextVideo():
    lobbyCode = request.json['lobbyCode']
    global lobbies
    for lobby in lobbies:
        if(lobby.getLobbyCode() == lobbyCode):
            return lobby.getNextVideo()

    return "Didn't find lobby"

@app.route('/getVideoQueue', methods=['POST'])
def getVideoQueue():
    lobbyCode = request.json['lobbyCode']
    global lobbies

    for lobby in lobbies:
        if(lobby.getLobbyCode() == lobbyCode):
            return JSONEncoder().encode(lobby.getVideoQueue())

    return "Didn't find lobby"

@app.route('/joinLobby', methods=['POST'])
def joinLobby():
    lobbyCode = request.json['lobbyCode'].upper()
    memberName = request.json['memberName']

    global lobbies

    lobbyWasFound = False

    for lobby in lobbies:
        if(lobby.getLobbyCode() == lobbyCode):
            # requested lobby exist, let them join
            lobby.addMember(memberName)
            lobbyWasFound = True
            print(lobby)
            break

    returnRes = {}

    if(not lobbyWasFound):
        returnRes = {'didJoin': False, 'lobbyCode': lobbyCode, 'memberName': memberName, 'Message': 'Invalid lobby ID'}
    else:
        returnRes = {'didJoin': True, 'lobbyCode': lobbyCode, 'memberName': memberName, 'Message': 'Success'}
        
    return json.dumps(returnRes)

@app.route('/leaveLobby', methods=['POST'])
def leaveLobby():
    lobbyCode = request.json['lobbyCode'].upper()
    memberName = request.json['memberName']

    lobbyWasFound = False
    global lobbies

    for lobby in lobbies:
        if(lobby.getLobbyCode() == lobbyCode):
            # requested lobby exist, remove them from the lobby
            lobby.deleteMember(memberName)
            lobbyWasFound = True
            print(lobby)
            break

    if(not lobbyWasFound):
        return "Invalid lobby ID"
    else:
        return memberName + " has been removed from " + lobbyCode

@app.route('/getLobbyInfo', methods=['GET'])
def getLobbyInfo():
    lobbyCode = request.args['lobbyCode']

    lobbyWasFound = False
    lobbyInfo = {}
    global lobbies

    for lobby in lobbies:
        if(lobby.getLobbyCode() == lobbyCode):
            return json.dumps(lobby.getInfo())

    return 'Lobby wasn\'t found'
    


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId) or isinstance(o, Timestamp) or isinstance(o, bytes) or isinstance(o, Lobby):
            return str(o)
        return json.JSONEncoder.default(self, o)


if __name__ == '__main__':
    startServer()
    socketio.run(app, debug=True)
