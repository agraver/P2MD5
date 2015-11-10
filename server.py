from computer import Computer
from crackTask import CrackTask
from slaveComputer import SlaveComputer
import urllib2
from urlparse import urlparse, parse_qs
import socket
import json
import sys
import ast

class Server:
    def __init__(self, port):
        #initiate a localhost server
        self.ip_address = '127.0.0.1'
        self.port = port
        self.sock = None
        self.resource = {"available": True, "amount": 100} #TODO
        self.computers = []
        self.slave_computers = []
        self.crack_tasks = []

    def addComputersFromMachinesTxt(self):
        try:
            filename = 'machines/machines%s.txt' % self.port
            input_file = open(filename, 'r')
            # Read string representitive of machine list.
            machines = input_file.read()
            # Parse string to list.
            machines = ast.literal_eval(machines)
            computers = [Computer(machine[0], machine[1]) for machine in machines]
            self.addComputers(computers)
        finally:
            pass
        return None

    def addComputers(self, computers):
        """
        These are the computers known to this Server.
        input:
            computers - list of Computer objects [Computer1, Computer2, ...]
        output:
            None
        """
        for computer in computers:
            if computer not in self.computers:
                self.computers.append(computer)
        return None

    def boot(self):
        self.address = (self.ip_address, self.port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.address)
        return None

    def listen(self):
        self.sock.listen(1)
        while True:
            # Wait for a connection
            print >>sys.stderr, 'waiting for a connection'
            connection, client_address = self.sock.accept()
            try:
                print >>sys.stderr, 'connection from', client_address
                # Receive the data in small chunks and retransmit it
                request_header = ""
                while True:
                    data = connection.recv(32)
                    if data:
                        request_header += data
                        #TODO understand why socket doesn't work without this
                        connection.sendall(data)
                    else:
                        break

                # print >>sys.stderr, '>>> the whole data >>>', request_header
                parse_result = self.parseRequestHeader(request_header)
                print >>sys.stderr, '>>> Header parse_result same as query_data>>>', parse_result
                self.handleRequest(parse_result)
            except:
                print >>sys.stderr, "An error has occured while listening." , sys.exc_info()

            finally:
                # Clean up the connection
                print "I closed the connection, yeeah."
                connection.close()

        return None

    def handleRequest(self, query_data):
        method, command, params = query_data
        print "inside handleRequest()"
        ## methods: GET, POST
        ## commands: resource[GET], resourcereply[POST], checkmd5[POST], answermd5[POST], crack[GET]
        ## params:
        ##    resource:[sendip,sendport,ttl,id,noask]
        ##    resourcereply:[ip, port, id, resource=100]
        ##    checkmd:[ip, port, id, md5, ranges, wildcard, symbolrange]
        ##        ranges: ["ax?o?ssss","aa","ab","ac","ad"]
        ##        wildcard: "?"
        ##        symbolrange: [[3,10],[100,150]]
        ##    answermd5:[ip, port, id, md5, result, resultString]
        ##        result: 0 - Success, 1 - String not Found, 2 - Didn't have enough time
        ##        resultString: saosdooe
        ##    crack:[md5]

        #TODO
        if method == "GET":
            print "GET branch"
            if command == "/resource":
                print "resource branch"
                # Do what computers do when they recieve a resource request
                # Like check if they have another process already running and
                # reply to the person of interest defined inside "sendip", "sendport"
                # variables
                task_id = params['id'][0]
                sendip = params['sendip'][0]
                sendport = params['sendport'][0]
                ttl = params['ttl'][0]
                try:
                    noask = params['noask']
                except Exception as e:
                    noask = []

                if self.checkResourceAvailable():
                    resource = self.getResourceAmount()
                else:
                    resource = 0

                print "sendip:", sendip, "sendport:", sendport, "task_id:", task_id, "resource:", resource
                self.sendResourceReply(sendip, sendport, task_id, resource)

                # Next step would be sending out requests to all the machines
                # that I, myself, as a Server, know from "machines.txt" file.
                if ttl > 0:
                    print "Sending out requests to minions"
                    self.sendResourceRequestToOthers(task_id, sendip, sendport, ttl, noask)
                else:
                    print "ttl has been exhausted. Resource request distribution has been terminated"

            if command == "/crack":
                self.startCracking(params["md5"])

        if method == "POST":
            if command == "/resourcereply":
                # TODO Save resourcereply POST data to self.computers.
                ip = params['ip']
                resource = params['resource']
                port = str(params['port'])
                id = params['id']
                for computer in self.computers:
                    if computer.port == port:
                        computer.resource_response = resource
                        computer = SlaveComputer(computer, resource)
                        self.slave_computers.append(computer)
                        break
                else:
                    computer = Computer(ip, port)
                    computer.resource_response = resource
                    computer = SlaveComputer(computer, resource)
                    self.slave_computers.append(computer)

                print "Computers from machines.txt"
                for c in self.computers:
                    print c.__str__()
                print "Slave computers"
                for c in self.slave_computers:
                    print c.__str__()

            if command == "/checkmd5": pass
            if command == "/answermd5": pass

    def checkResourceAvailable(self):
        return self.resource['available']

    def getResourceAmount(self):
        return self.resource['amount']

    def sendResourceReply(self, sendip, sendport, task_id, resource):
        ##    resourcereply:[ip, port, id, resource=100]
        print "inside sendResourceReply()"
        ip_address = self.ip_address
        port = self.port
        # resource = {available: True/False, amount: 100(const)}
        url = "http://%s:%s/resourcereply" %(sendip, sendport)
        data = json.dumps({"ip":ip_address, "port":port, "id":task_id, "resource":resource})
        print "url:", url
        print "data:", data
        req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        print "made the request"
        response_stream = urllib2.urlopen(req)
        print "opened the request"
        response_stream.close()
        print "closed the request"

    def sendResourceRequestToOthers(self, task_id, sendip, sendport, ttl, noask):
        # this is a modified with noask parameter version of the original MasterResourceRequest
        # Gather your brothers from the "machines.txt" file and ask them to ask their brothers
        # To join in a common effort with the master P2MD5 machine.

        # Lower ttl count by 1
        ttl = int(ttl) - 1

        # Add senders computers ip to noask list, so there would be no duplicate requests to this machine
        noask.append("%s_%s" % (self.ip_address, self.port))

        for computer in self.computers:
            computer.sendResourceRequest(sendip, sendport, ttl, task_id, noask)
            print self.ip_address+" sent to " + computer.ip_address + ":" + computer.port

    def startCracking(self, md5):
        #Start with a resource request as the initiator, the legendary P2MD5 master machine
        #Prepare the request, params needed: ttl
        task_id = self.generateId(md5)
        task = CrackTask(task_id, md5, self.ip_address, self.port)
        self.addcrackTaskToList(task)
        ttl = 5
        self.sendMasterResourceRequest(ttl, task_id)
        #TODO wait for some time to collect responses and divide the task between servant machines.
        pass

    def addcrackTaskToList(self, crack_task):
        # TODO should be a function to add crackTasks as to update with received ones and
        # avoid something that might override the wrong way or duplicate.

        # TODO bonus for thinking: use datastructure for optimal result. (YAGNI?)

        #things to avoid: duplicate ids
        for task in self.crack_tasks:
            if crack_task.id == task.id:
                pass
                #case to check if needs update, ie contains answer inside.
                #but!! crackTask were meant to be with the same id but different
                #divisions of the same task ie Ranges and

    def sendMasterResourceRequest(self, ttl, task_id):
        sendip = self.ip_address
        sendport = self.port
        noask = []
        for computer in self.computers:
            computer.sendResourceRequest(sendip, sendport, ttl, task_id, noask)

    def generateId(self, md5):
        #assume md5 is a string
        #TODO generate a more unique md5 identificator
        return md5[:5] + "420"

    def parseRequestHeader(self, request_header):
        """
        method        GET
        path          '/resource?sendip=55.66.77.88&sendport=6788&ttl=5&id=wqeqwe23&noask=11.22.33.44_345&noask=111.222.333.444_223'
        version       'HTTP/1.1'

        command       '/resource'
        params        {'noask': ['11.22.33.44_345', '111.222.333.444_223'], 'sendip': ['55.66.77.88'], 'id': ['wqeqwe23'], 'sendport': ['6788'], 'ttl': ['5']}
        """
        print request_header

        # GET REQUEST
        lines = request_header.splitlines()
        first_line = lines[0]
        method, path, version = first_line.split()
        command, params = self.parsePath(path)

        # POST REQUEST
        if method == "POST":
            # Its a json string inside the list
            posted_data_string = lines[-1:][0]
            params = json.loads(posted_data_string)
            print "Parsed data is ", params
        return method, command, params

    def parsePath(self, path):
        q_data = urlparse(path)
        query = q_data.query
        return q_data.path, parse_qs(query)

    def close(self):
        pass
