class CrackTask:
    def __init__(self, id, md5, masterIp, masterPort):
        self.md5 = md5
        self.id = id
        self.masterIp = masterIp
        self.masterPort = masterPort
        self.answer = None
        self.ranges = None
        self.wildcard = None
