from computer import Computer
from slaveComputer import SlaveComputer

class CrackTask:
    def __init__(self, master_computer, md5):
        self.task_id = self.generateId(md5)
        self.answer = None
        self.ranges = None
        self.wildcard = None
        self.master_computer = master_computer
        self.slave_computers = {} # {'<ip_port>':<SlaveComputer>}

    def solve(self):
        print "inside main function of CrackTask"
        # take the crack_task and count computers
        # divide the cracktask accordingly, compose all the strings
        # send out the crack_task parts to the computers
        # slaveComputers receive and start cracking on a separate thread

        pass

    def generateId(self, md5):
        #assume md5 is a string
        #TODO generate a more unique md5 identificator
        return md5[:5] + "420"

    def getSlaveKey(self, computer):
        ip = computer.ip_address
        port = computer.port
        return "%s_%s" % (ip, port)

    def splitBetweenSlaves(self,):
        pass

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
