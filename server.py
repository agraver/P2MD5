from computer import Computer
from crackTask import CrackTask
from slaveComputer import SlaveComputer
from multiprocessing import Process
from action import Action
import urllib2
from urlparse import urlparse, parse_qs
import socket
import json
import sys
import time
import ast

class Server:
    def __init__(self, port):
        #initiate a localhost server
        self.ip_address = '127.0.0.1'
        self.port = port
        self.sock = None
        self.resource = {"available": True, "amount": 100} #TODO

        # {'<ip>_<port>':<Computer>}
        self.known_computers = {}
        # {'crack_task_id':<CrackTask>}
        self.crack_tasks = {}
        # Set of task ids, which I have already sent a resourcereply
        self.responded_task_ids = set()
        # {'<ip>_<port>'}
        self.responded_computers = set()
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
                # Just print out all crack_tasks
                for crack_task in self.crack_tasks.values():
                    print "Task %s has:" % str(crack_task.task_id)
                    for slave in crack_task.slave_computers.values():
                        print "    %s"%str(slave)

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
        print "made the request"
        try:
            req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
            response_stream = urllib2.urlopen(req).read()
            print "opened the request"
            response_stream.close()
            print "closed the request"
        except urllib2.HTTPError, err:
            if err.code == 404:
                print "Page not found!"
            elif err.code == 403:
                print "Access denied!"
            else:
                print "Something happened! Error code", err.code
        except urllib2.URLError, err:
            print "Some other error happened:", err.reason


    def sendResourceRequestToOthers(self, task_id, sendip, sendport, ttl, noask):
        # this is a modified with noask parameter version of the original MasterResourceRequest
        # Gather your brothers from the "machines.txt" file and ask them to ask their brothers
        # To join in a common effort with the master P2MD5 machine.

        if ttl <= 0:
            return None
        else:
            # Lower ttl count by 1
            ttl = int(ttl) - 1

        # Add senders computers ip to noask list, so there would be no duplicate requests to this machine
        computer_address = "%s_%s" % (self.ip_address, self.port)
        if computer_address not in noask:
            noask.append(computer_address)

        for computer in self.known_computers.values():
            computer.sendResourceRequest(sendip, sendport, ttl, task_id, noask)
            print self.ip_address+" sent to " + computer.ip_address + ":" + computer.port

    def f(self, arg):
        print "Going to sleep for 5 sec... " + arg
        time.sleep(1)
        print "4"
        time.sleep(1)
        print "3"
        time.sleep(1)
        print "2"
        time.sleep(1)
        print "1"
        time.sleep(1)
        print "Should send out checkmd5 request now", self.crack_tasks

    def startCracking(self, md5):
        #Start with a resource request as the initiator, the legendary P2MD5 master machine
        #Prepare the request, params needed: ttl
        task_id = self.generateId(md5)
        task = CrackTask(task_id)
        ttl = 5
        self.sendMasterResourceRequest(ttl, task_id)
        """
        t1 = Process(target=self.f, args=('bob',))
        t2 = Process(target=self.sendMasterResourceRequest, args=(ttl, task_id,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        """
        #TODO wait for some time to collect responses and divide the task between servant machines.
        #TODO use self.slave_computers

    def sendMasterResourceRequest(self, ttl, task_id):
        sendip = self.ip_address
        sendport = self.port
        noask = []
        for computer in self.known_computers.values():
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

    def __str__(self):
        return self.ip_address + '_' + str(self.port)
