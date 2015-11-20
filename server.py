from computer import Computer
from crackTask import CrackTask
from slaveComputer import SlaveComputer
import threading
from action import Action
import urllib2
from urlparse import urlparse, parse_qs
import socket
import json
import sys
import copy
import ast

class Server:
    def __init__(self, port):
        #initiate a localhost server
        #TODO refactor for deployment on different IPs
        self.ip_address = '127.0.0.1'
        self.port = port
        self.sock = None
        self.resource = {"available": True, "amount": 100} #TODO
        self.myself = Computer(self.ip_address, self.port)
        self.known_computers = {} # {'<ip>_<port>':<Computer>}
        self.crack_tasks = {} # {'crack_task_id':<CrackTask>}

        # Set of task ids, which I have already sent a resourcereply
        self.responded_task_ids = set()  # {'<task_id>'}
        self.responded_computers = set() # {'<ip>_<port>'}

        # Commands: resource[GET], resourcereply[POST], checkmd5[POST], answermd5[POST], crack[GET]
        # Action handlers. Usage: self.handle.<command>(params)
        self.handle = Action()

        self.addComputersFromMachinesTxt()

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
            ip = computer.ip_address
            port = computer.port
            key = "%s_%s" % (ip, port)
            if key not in self.known_computers.keys():
                self.known_computers[key] = computer
        return None

    def boot(self):
        self.address = (self.ip_address, self.port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.sock.settimeout(1) #just times out in a second after opening the socket
        self.sock.bind(self.address)
        return None

    def listen(self):
        self.sock.listen(10)
        while True:
            print >>sys.stderr, 'waiting for a connection'
            connection, client_address = self.sock.accept()
            try:
                print >>sys.stderr, 'connection from', client_address
                request_header = ""
                data = connection.recv(4096)
                request_header += data
                connection.sendall(data)
                connection.close()
                parse_result = self.parseRequestHeader(request_header)
                print >>sys.stderr, '>>> Header parse_result (same as query_data) >>>', parse_result
                t = threading.Thread(target=self.handleRequest, args=(parse_result,))
                t.start()
            except:
                print >>sys.stderr, "An error has occured while listening." , sys.exc_info()

        return None

    def handleRequest(self, query_data):
        method, command, params = query_data
        print "inside handleRequest() thread version"
        ## methods: GET, POST
        ## commands: resource[GET], resourcereply[POST], checkmd5[POST], answermd5[POST], crack[GET]
        ## params:
        ##    resource:[sendip,sendport,ttl,id,noask]
        ##    resourcereply:[ip, port, id, resource=100]
        ##    checkmd5:[ip, port, id, md5, ranges, wildcard, symbolrange]
        ##        ranges: ["ax?o?ssss","aa","ab","ac","ad"]
        ##        wildcard: "?"
        ##        symbolrange: [[3,10],[100,150]]
        ##    answermd5:[ip, port, id, md5, result, resultString]
        ##        result: 0 - Success, 1 - String not Found, 2 - Didn't have enough time
        ##        resultString: saosdooe
        ##    crack:[md5]

        if method == "GET":
            print "GET branch"
            # Master -> Slave
            if command == "/resource":
                self.handle.resource(self, params)
            # Master -> Slave
            if command == "/crack":
                self.handle.crack(self, params)

        if method == "POST":
            # Slave -> Master
            if command == "/resourcereply":
                self.handle.resourcereply(self, params)
            # Master -> Slave
            if command == "/checkmd5":
                self.handle.checkmd5(self, params)
            # Slave -> Master
            if command == "/answermd5":
                self.handle.answermd5(self, params)

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
        print "next I'm going to send the resourceReply"
        try:
            req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
            response_stream = urllib2.urlopen(req)
            response_stream.close()
        except urllib2.HTTPError, err:
            print "HTTPError", err.code
        except urllib2.URLError, err:
            print "URLError", err.reason
        except socket.timeout, e:
            raise e


    def sendResourceRequestToOthers(self, task_id, sendip, sendport, ttl, noask):
        # this is a modified with noask parameter version of the original MasterResourceRequest
        # Gather your brothers from the "machines.txt" file and ask them to ask their brothers
        # To join in a common effort with the master P2MD5 machine.
        print "Inside sendResourceRequestToOthers()"
        ttl = int(ttl)
        if ttl < 1:
            return None
        else:
            ttl = ttl - 1

        # Add senders computers ip to noask list, so there would be no duplicate requests to this machine
        computer_address = "%s_%s" % (self.ip_address, self.port)
        if computer_address not in noask:
            noask.append(computer_address)

        for computer in self.known_computers.values():
            recepient_address = "%s_%s" % (computer.ip_address, computer.port)
            if recepient_address in noask:
                continue
            computer.sendResourceRequest(sendip, sendport, ttl, task_id, noask)
            print self.ip_address+" sent ResourceRequest to " + computer.ip_address + ":" + computer.port
        print "sendResourceRequestToOthers() is complete"

    def startCracking(self, md5):
        task = CrackTask(self.myself, md5) #adding myself as the master computer to respond to through class methods.
        task_id = task.task_id
        self.crack_tasks[task_id] = task

        ttl = 5
        self.sendMasterResourceRequest(ttl, task_id)
        print "self.sendMasterResourceRequest(ttl, task_id) successful"

        t = threading.Timer(5, self.printCrackTask, args=(task_id,))
        t.start()
        t.join() # wait until finished

        task_deepcopy = copy.deepcopy(task)
        print "made the deepcopy"
        t = threading.Thread(target=self.masterCrackTaskProcess, args=(task_deepcopy,))
        t.start()

    def masterCrackTaskProcess(self, crackTask):
        print "inside masterCrackTaskProcess()"
        crackTask.solve()

    def sendMd5Answer(self, master_ip, master_port, task_id, md5, result, resultstring):
        ip_address = self.ip_address
        port = self.port
        url = "http://%s:%s/answermd5" %(master_ip, master_port)
        data = json.dumps({"ip":ip_address, "port":port, "id":task_id,\
                        "md5":md5, "result":result, "resultstring":resultstring})

        req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        response_stream = urllib2.urlopen(req)
        response_stream.close()

    def printCrackTask(self, task_id):
        crack_task = self.crack_tasks[task_id]
        print "here's the result: "
        print crack_task
        for slave in crack_task.slave_computers.values():
            print "    %s"%str(slave)

    def sendMasterResourceRequest(self, ttl, task_id):
        sendip = self.ip_address
        sendport = self.port
        noask = []
        for computer in self.known_computers.values():
            computer.sendResourceRequest(sendip, sendport, ttl, task_id, noask)


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
            # print "Parsed data is ", params
        return method, command, params

    def parsePath(self, path):
        q_data = urlparse(path)
        query = q_data.query
        return q_data.path, parse_qs(query)

    def close(self):
        pass

    def __str__(self):
        return self.ip_address + '_' + str(self.port)
