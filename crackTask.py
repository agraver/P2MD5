from computer import Computer
from slaveComputer import SlaveComputer
import threading
import time

class CrackTask:
    def __init__(self, master_computer, md5):
        self.md5 = md5
        self.task_id = self.generateId(md5)
        self.answer = None
        self.divided_ranges = {} # ie {"<ip_port>":["?","??","???","????","????a"], "<ip_port>":["????b", "????c", "????d"],"<ip_port>": ["????d","????e","????f"],....}
        self.wildcard = "?" # ie "?"
        self.symbolrange = [[32,126]] # i.e [[1,10],[95,100]]

        self.master_computer = master_computer
        self.slave_computers = {} # {'<ip_port>':<SlaveComputer>}
        self.answered_computers = set() # {'<ip_port>'}

        self.failed_templates = []

        self.startTime = time.time()
        self.solved = False
        self.locked = False

        self.LENGTH_LIMIT = 4 # max length of the word that we're going to bruteforce
        self.TIMEOUT = 120
        #TODO address the unsolvable case where the answer lies outside the lenght_limit
        # such that we've looked through all the ranges and haven't found the answer

    def solve(self):
        print "inside main solving function of CrackTask"
        slave_count = self.countSlaves()
        # divide the cracktask accordingly, compose all the strings
        self.divided_ranges = self.MD5IntoDividedRanges(slave_count, self.LENGTH_LIMIT)
        print self.divided_ranges

        # send out the crack_task parts to the computers
        self.sendTasks()
        # slaveComputers receive and start cracking on a separate thread

    def sendTasks(self):
        for ip_port in self.divided_ranges.keys():
            self.slave_computers[ip_port].sendTask(
                self.master_computer.ip_address,
                self.master_computer.port,
                self.task_id,
                self.md5,
                self.divided_ranges[ip_port],
                self.wildcard,
                self.symbolrange
                )

    def MD5IntoDividedRanges(self, slave_count, length_limit):
        symbols_count = self.countSymbolRange()

        # total_search_space = 0
        # for i in range(length_limit+1):
        #     total_search_space += symbols_count**i
        #
        # search_space_per_slave = total_search_space / slave_count

        if self.failed_templates:
            print "printing out the failed_templates"
            print self.failed_templates


        if (slave_count > symbols_count):
            print ":(((( we have to split the task smarter"
            return None

        explicit_symbol_range = []
        for r in self.symbolrange:
            partial_symbol_range = map((lambda x: chr(x)), (range(r[0], r[1]+1)))
            explicit_symbol_range += partial_symbol_range

        #Exclude wildcard as it creates an unwanted template full of wildcards
        explicit_symbol_range.remove(self.wildcard)

        lesser_range = []
        for i in range(1, length_limit):
            template = self.wildcard * i
            lesser_range.append(template)

        wider_range = map((lambda x: self.wildcard*(length_limit-1) + x), explicit_symbol_range)

        whole_range = lesser_range + wider_range

        # removing failed_templates
        whole_range = list(set(self.failed_templates).symmetric_difference(whole_range))
        # restoring sorted order so that ?, ??, ??? etc. are in front
        whole_range.sort()

        def chunkIt(seq, num):
            avg = len(seq) / float(num)
            out = []
            last = 0.0
            while last < len(seq):
                out.append(seq[int(last):int(last + avg)])
                last += avg
            return out

        print "slave_count: " + str(slave_count)
        pre_result = list(chunkIt(whole_range, slave_count))

        # print "pre_result: ", pre_result
        # print "slave_computers"

        i = 0
        divided_ranges = {}
        for slave_key in self.slave_computers.keys():
            divided_ranges[slave_key] = pre_result[i]
            i += 1

        return divided_ranges

    def countSymbolRange(self):
        symbolrange = self.symbolrange
        symbols_total = 0
        for r in symbolrange:
            symbols_total += r[1] - r[0] + 1
        return symbols_total

    def countSlaves(self):
        return len(self.slave_computers.keys())

    def generateId(self, md5):
        #TODO maybe think of a shorter way to represent a md5 uniquely
        # yet consistently across other servers that may generate it
        return md5

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

    def everyoneResponded(self):
        for ip_port in self.divided_ranges.keys():
            if ip_port not in self.answered_computers:
                return False
        return True

    def timedOut(self):
        return (time.time() - self.startTime) > self.TIMEOUT


    def __str__(self):
        return 'CrackTask ' + self.task_id +' has slaves'+ str(self.slave_computers.values())
