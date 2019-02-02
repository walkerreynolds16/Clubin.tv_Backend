class Lobby:

    def __init__(self, lobbyCode):
        self.lobbyCode = lobbyCode
        self.videoQueue = []
        self.memberList = []
        self.currentVideo = {}

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
        newVid = self.videoQueue.pop(0)
        self.currentVideo = newVid
        return newVid

    def getCurrentVideo(self):
        if(self.currentVideo is {}):
            return "No video playing"
        else:
            return self.currentVideo

    def addVideoToQueue(self, videoId):
        self.videoQueue.append(videoId)

    def addMember(self, memberName):
        self.memberList.append(memberName)

    def deleteMember(self, memberName):
        self.memberList.remove(memberName)
