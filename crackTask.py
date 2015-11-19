from computer import Computer
from slaveComputer import SlaveComputer

class CrackTask:
    def __init__(self, master_computer, md5):
        self.md5 = md5
        self.task_id = self.generateId(md5)
        self.answer = None
        self.divided_ranges = None # ie {"<ip_port>":["?","??","???","????","????a"], "<ip_port>":["????b", "????c", "????d"],"<ip_port>": ["????d","????e","????f"],....}
        self.wildcard = "?" # ie "?"
        self.symbolrange = [[32,126]] # i.e [[1,10],[95,100]]
        self.master_computer = master_computer
        self.slave_computers = {} # {'<ip_port>':<SlaveComputer>}

    def solve(self):
        print "inside main solving function of CrackTask"
        slave_count = self.countSlaves()
        # divide the cracktask accordingly, compose all the strings

        #initialize wildcard
        #initialize symbolrange

        length_limit = 5
        self.divided_ranges = self.MD5IntoRanges(slave_count, length_limit)
        print self.divided_ranges

        # send out the crack_task parts to the computers
        # slaveComputers receive and start cracking on a separate thread
        self.md5Crack(self.md5, "template")
        pass

    def md5Crack(self, md5, template):
        pass

    def MD5IntoRanges(self, slave_count, length_limit):
        symbols_count = self.countSymbolRange()

        # total_search_space = 0
        # for i in range(length_limit+1):
        #     total_search_space += symbols_count**i
        #
        # search_space_per_slave = total_search_space / slave_count

        if (slave_count > symbols_count):
            print ":(((( we have to split the task smarter"
            return None

        explicit_symbol_range = []
        for r in self.symbolrange:
            partial_symbol_range = map((lambda x: chr(x)), (range(r[0], r[1]+1)))
            explicit_symbol_range += partial_symbol_range

        def chunkIt(seq, num):
            avg = len(seq) / float(num)
            out = []
            last = 0.0

            while last < len(seq):
                out.append(seq[int(last):int(last + avg)])
                last += avg

            return out

        print "slave_count: " + str(slave_count)
        pre_result = list(chunkIt(explicit_symbol_range, slave_count))

        lesser_range = []
        for i in range(1, length_limit):
            lesser_range.append(self.wildcard * i)

        wide_ranges = []
        for r in pre_result:
            w_range = map((lambda x: self.wildcard*(length_limit-1) + x), r)
            wide_ranges.append(w_range)

        wide_ranges[0] += lesser_range

        i = 0
        divided_ranges = {}
        for slave_key in self.slave_computers.keys():
            divided_ranges[slave_key] = wide_ranges[i]
            i += 1

        return divided_ranges

    def countSymbolRange(self):
        symbolrange = self.symbolrange
        symbols_total = 0
        for r in symbolrange:
            symbols_total = r[1] - r[0] + 1
        return symbols_total

    def countSlaves(self):
        return len(self.slave_computers.keys())

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
