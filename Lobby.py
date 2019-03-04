import json

class Lobby:

    def __init__(self, lobbyCode):
        self.lobbyCode = lobbyCode
        self.videoQueue = []
        self.memberList = []
        self.currentVideo = {} # keep track of current DJ and video

    def __str__(self):
        return self.lobbyCode + " - " + str(self.memberList)

    def getInfo(self):
        data = {'lobbyCode': self.lobbyCode, 'videoQueue': self.videoQueue, 'memberList': self.memberList, 'currentVideo': self.getCurrentVideo()}
        return data

    def getLobbyCode(self):
        return self.lobbyCode

    def getVideoQueue(self):
        return self.videoQueue

    def getNextVideo(self):
        if(len(self.videoQueue) > 0):
            newVid = self.videoQueue.pop(0)
            self.currentVideo = newVid
            return newVid
        else:
            return -1
        

    def getCurrentVideo(self):
        return self.currentVideo

    def setCurrentVideo(self, video, memberName):
        if(video != None and memberName != None):
            print('video: ' + json.dumps(video))
            print('memberName: ' + memberName)
            self.currentVideo = {"memberName": memberName, "videoId": video['videoId'], "channelName": video['channelName'], "videoTitle": video['videoTitle']}
        else:
            self.currentVideo = {}

    def addVideoToQueue(self, video, memberName):
        self.videoQueue.append({"video": video, 'memberName': memberName})

    def addMember(self, memberName):
        self.memberList.append(memberName)

    def deleteMember(self, memberName):
        self.memberList.remove(memberName)
