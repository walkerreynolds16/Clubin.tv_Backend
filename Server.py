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
clients = []


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
    for l in lobbies:
        print(l)

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
    memberName = request.json['memberName']
    video = request.json['video']

    lobby = getLobbyObject(lobbyCode)
    client = getClientObject(lobbyCode)

    if(lobby != None):
        if(lobby.getCurrentVideo() == {}):
            lobby.setCurrentVideo(video, memberName)

            if(client != None):
                socketio.emit('Event_startVideo', {"currentVideo": {"memberName": memberName, 'videoId': video['videoId'], 'videoTitle': video['videoTitle'], 'channelName': video['channelName']}}, room=client['androidRequestId'])            

                


        else:
            lobby.addVideoToQueue(video, memberName)

        # Retrieve lobby info to send to the lobby android client
        lobbyInfo = lobby.getInfo()
        if(client != None):
            socketio.emit('Event_lobbyUpdate', lobbyInfo, room=client['androidRequestId'])

            for c in client['mobileClients']:
                    socketio.emit('Event_lobbyUpdate', lobbyInfo, room=c['requestId'])

        return JSONEncoder().encode(lobby.getVideoQueue())

    else:
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

    lobby = getLobbyObject(lobbyCode)
    client = getClientObject(lobbyCode)

    returnRes = {}

    if(lobby != None):
        # requested lobby exist, let them join
        lobby.addMember(memberName)
        lobbyInfo = lobby.getInfo()

        if(client != None):
            socketio.emit('Event_lobbyUpdate', lobbyInfo, room=client['androidRequestId'])

            for c in client['mobileClients']:
                socketio.emit('Event_lobbyUpdate', lobbyInfo, room=c['requestId'])

        returnRes = {'didJoin': True, 'lobbyCode': lobbyCode, 'memberName': memberName, 'Message': 'Success'}

    else:
        returnRes = {'didJoin': False, 'lobbyCode': lobbyCode, 'memberName': memberName, 'Message': 'Invalid lobby ID'}
        
    return json.dumps(returnRes)

@app.route('/leaveLobby', methods=['POST'])
def leaveLobby():
    # TODO added socket emit to update client
    lobbyCode = request.json['lobbyCode'].upper()
    memberName = request.json['memberName']

    print("Lobby Code = " + lobbyCode)
    print("Member Name = " + memberName)
    

    lobby = getLobbyObject(lobbyCode)
    client = getClientObject(lobbyCode)

    print("Member List = " + str(lobby.getInfo()["memberList"]))

    if(lobby != None):
        # requested lobby exist, remove them from the lobby
        lobby.deleteMember(memberName)

        lobbyInfo = lobby.getInfo()

        if(client != None):
            socketio.emit('Event_lobbyUpdate', lobbyInfo, room=client['androidRequestId'])

            for c in client['mobileClients']:
                socketio.emit('Event_lobbyUpdate', lobbyInfo, room=c['requestId'])

            for mClient in client['mobileClients']:
                if(mClient['memberName'] == memberName):
                    client['mobileClients'].remove(mClient)
            

        print(memberName + " has been removed from " + lobbyCode)
        return memberName + " has been removed from " + lobbyCode
    else:
         return "Invalid lobby ID"


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
    


@socketio.on('Event_connection')
def clientConnection(data):
    print(request.sid + " connected from android")
    clients.append({'lobbyCode': data['lobbyCode'], 'androidRequestId': request.sid, 'mobileClients': []})

@socketio.on('Event_mobileConnection')
def mobileClientConnection(data):
    print(request.sid + " connected from mobile")

    global clients

    lobby = getLobbyObject(data['lobbyCode'])

    for client in clients:
        if(client['lobbyCode'] == data['lobbyCode']):
            client['mobileClients'].append({'requestId': request.sid, 'memberName': data['memberName']})

            for c in client['mobileClients']:
                socketio.emit('Event_lobbyUpdate', lobby.getInfo(), room=c['requestId'])

    print(clients)            

@socketio.on('Event_disconnection')
def clientDisconnection(data):
    print(request.sid + " disconnected")

    global clients

    lobby = getLobbyObject(data['lobbyCode'])

    for c in clients:
        if(c['lobbyCode'] == data['lobbyCode']):
            clients.remove(c)

            for c in client['mobileClients']:
                socketio.emit('Event_lobbyUpdate', lobby.getInfo(), room=c['requestId'])

@socketio.on('Event_endVideo')
def endVideo(data):
    print(request.sid + " has ended a video")
    print(data['lobbyCode'])
    print(data['currentVideo'])

    lobby = getLobbyObject(data['lobbyCode'])
    client = getClientObject(data['lobbyCode'])

    if(lobby != None):
        newVid = lobby.getNextVideo()
        lobby.setCurrentVideo(None, None)

        if(newVid != -1):
            lobby.setCurrentVideo(newVid['video'], newVid['memberName'] )

            if(client != None):
                socketio.emit('Event_startVideo', {"currentVideo": {"memberName": newVid['memberName'], 'videoId': newVid['video']['videoId'], 'videoTitle': newVid['video']['videoTitle'], 'channelName': newVid['video']['channelName']}}, room=client['androidRequestId'])

                for c in client['mobileClients']:
                    socketio.emit('Event_lobbyUpdate', lobby.getInfo(), room=c['requestId'])


def getLobbyObject(lobbyCode):
    global lobbies

    for lobby in lobbies:
        if(lobby.getLobbyCode() == lobbyCode):
            return lobby

    return None

def getClientObject(lobbyCode):
    global clients

    for c in clients:
        if(c['lobbyCode'] == lobbyCode):
            return c

    return None

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId) or isinstance(o, Timestamp) or isinstance(o, bytes) or isinstance(o, Lobby):
            return str(o)
        return json.JSONEncoder.default(self, o)


if __name__ == '__main__':
    startServer()
    socketio.run(app, debug=True)
