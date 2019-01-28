class Lobby:

    def __init__(self, lobbyCode):
        self.lobbyCode = lobbyCode
        self.videoQueue = []

    def __str__(self):
        return self.lobbyCode

    def getLobbyCode(self):
        return self.lobbyCode

    def getVideoQueue(self):
        return self.videoQueue

    def getNextVideo(self):
        return self.videoQueue.pop(0)

    def addVideoToQueue(self, videoId):
        self.videoQueue.append(videoId)
