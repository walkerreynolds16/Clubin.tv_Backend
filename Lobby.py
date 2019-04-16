import json


class Lobby:

    def __init__(self, lobbyCode):
        self.lobbyCode = lobbyCode
        self.videoQueue = []
        self.memberList = []
        self.currentVideo = {}  # keep track of current DJ and video
        self.playingVideo = False
        self.skippers = []

    def __str__(self):
        return self.lobbyCode + " - " + str(self.memberList)

    def getInfo(self):
        data = {'lobbyCode': self.lobbyCode, 'videoQueue': self.videoQueue, 'memberList': self.memberList,
                'currentVideo': self.getCurrentVideo(), 'playingVideo': self.playingVideo, 'skippers': self.skippers}
        return data

    def setInfo(self, info):
        self.videoQueue = info['videoQueue']
        self.memberList = info['memberList']
        self.currentVideo = info['currentVideo']
        self.playingVideo = info['playingVideo']
        self.skippers = info['skippers']

    def getLobbyCode(self):
        return self.lobbyCode

    def getVideoQueue(self):
        return self.videoQueue

    def setVideoQueue(self, videoQueue):
        self.videoQueue = videoQueue

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
            self.currentVideo = {"memberName": memberName,
                                 "videoId": video['videoId'], "channelName": video['channelName'], "videoTitle": video['videoTitle']}
        else:
            self.currentVideo = {}

    def addVideoToQueue(self, video, memberName):
        self.videoQueue.append(
            {'memberName': memberName, 'video': {'videoId': video['videoId'], 'videoTitle': video['videoTitle'], 'channelName': video['channelName']}})

    def addMember(self, memberName):
        self.memberList.append(memberName)

    def deleteMember(self, memberName):
        self.memberList.remove(memberName)

    def getPlayingVideo(self):
        return self.playingVideo

    def setPlayingVideo(self, playing):
        self.playingVideo = playing

    def getSkippers(self):
        return self.skippers
    
    def setSkippers(self, newList):
        self.skippers = newList

    def voteToSkip(self, memberName):
        if(memberName in self.skippers):
            self.skippers.remove(memberName)
        else:
            self.skippers.append(memberName)

    def getMemberList(self):
        return self.memberList