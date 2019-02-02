class Lobby:

    def __init__(self, lobbyCode):
        self.lobbyCode = lobbyCode
        self.videoQueue = []
        self.memberList = []

    def __str__(self):
        return self.lobbyCode + " - " + str(self.memberList)

    def getLobbyCode(self):
        return self.lobbyCode

    def getVideoQueue(self):
        return self.videoQueue

    def getNextVideo(self):
        return self.videoQueue.pop(0)

    def addVideoToQueue(self, videoId):
        self.videoQueue.append(videoId)

    def addMember(self, memberName):
        self.memberList.append(memberName)

    def deleteMember(self, memberName):
        self.memberList.remove(memberName)
