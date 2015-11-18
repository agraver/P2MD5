from computer import Computer
from slaveComputer import SlaveComputer

class CrackTask:
    def __init__(self, master_computer, task_id):
        self.task_id = task_id
        self.answer = None
        self.ranges = None
        self.wildcard = None
        # {'<Key>':<SlaveComputer>}
        self.master_computer = None
        self.slave_computers = {}

    def setMD5(self, md5):
        self.md5 = md5

    def getSlaveKey(self, computer):
        ip = computer.ip_address
        port = computer.port
        return "%s_%s" % (ip, port)

    def hasSlave(self, computer):
        """
            If CrackTask has computer stored in self.slave_computers
            returns True/False
        """
        key = self.getSlaveKey(computer)
        return key in self.slave_computers.keys()

    def addSlave(self, computer):
        """
            Add slave computer to self.slave_computers
            returns None
        """
        key = self.getSlaveKey(computer)
        self.slave_computers[key] = computer

    def __str__(self):
        return 'CrackTask ' + self.task_id +' has slaves'+ str(self.slave_computers.values())
