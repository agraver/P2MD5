class CrackTask:
    def __init__(self, task_id, md5, masterIp, masterPort):
        self.md5 = md5
        self.task_id = task_id
        self.masterIp = masterIp
        self.masterPort = masterPort
        self.answer = None
        self.ranges = None
        self.wildcard = None
