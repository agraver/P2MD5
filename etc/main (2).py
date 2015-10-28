import json
import urllib2
import socket
import sys
from urlparse import urlparse, parse_qs

def main():
    #TODO how to undbind the sockets?
    my_machine = Server(10007)
    my_machine.addComputersFromMachinesTxt()
    my_machine.boot()
    my_machine.listen() #should decide what to do with incoming GET/POST requests

class Server:
    def __init__(self, port):
        #initiate a localhost server
        self.ip_address = '127.0.0.1'
        self.port = port
        self.sock = None
        self.resource =  {"available": True, "amount": 100}
        self.computers = []
        self.crackTasks = []

    def addComputersFromMachinesTxt(self):
        try:
            # input_file = open('machines.txt', 'r')
            # machines = f.read()
            machines = [["localhost", "10001"], ["127.0.0.1", "10002"], ["localhost", "10002"]]
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
                        connection.sendall(data) #TODO understand why socket doesn't work without this
                    else:
                        break

                # print >>sys.stderr, '>>> the whole data >>>', request_header
                parse_result = self.parseRequestHeader(request_header)
                self.handleRequest(parse_result)
            except:
                print >>sys.stderr, "An error has occured while listening."

            finally:
                # Clean up the connection
                print "I closed the connection, yeeah."
                connection.close()

        return None

    def handleRequest(self, query_data):
        method, command, params = query_data

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
            if command == "resource":
                # Do what computers do when they recieve a resource request
                # Like check if they have another process already running and
                # reply to the person of interest defined inside "sendip", "sendport"
                # variables
                self.sendReply()

                # Next step (later) would be sending out requests to all the machines
                # that I, myself, as a Server, know from "machines.txt" file.
                self.sendResourceRequestToOthers()

            if command == "crack":
                self.startCracking(params["md5"])

        if method == "POST":
            if command == "resourcereply": pass
            if command == "checkmd5": pass
            if command == "answermd5": pass

        """
        if parse_result == "resourceRequest":
            #TODO what to do in case of receiving a request about resource availability
            pass
        elif (parse_result == "jobTask"):
            #TODO what to do in case we receive a task to solve
            pass

        if command == "POST":
            #TODO POST requests are related to accepting answers from other computers.
            pass

        if command == "GET":

            print "Got a GET request > ", command, params
        """
        pass

    def sendReply(self, Computer):
        ##    resourcereply:[ip, port, id, resource=100]
        ip = self.ip
        port = self.port


        Computer.getId()
        if self.resource[avalailable]: # resource = {available: True/False, amount: 100(const)}
            #if needed create a new Computer objects
            #and access function Computer.sendReply()

        #TODO Construct JsonData here
        json = json.dumps({"ip":Computer.getIp(), "port":Computer.getPort(), "id":"", "resource":""})


        urllib2.post("http://11.22.33.44:20491/resourcereply", JsonData)

        # TODO urllib2 action goes inside of here

    def sendRequestToOthers(self):
        # Gather your brothers from the "machines.txt" file and ask them to ask their brothers
        # To join in a common effort with the master P2MD5 machine.

        # this is a modified with noask parameter version of the original MasterResourceRequest
        pass

    def startCracking(self, md5):
        #Start with a resource request as the initiator, the legendary P2MD5 master machine
        #Prepare the request, params needed: noask:  ttl
        id = self.generateId(md5)
        task = CrackTask(id, md5, self.ip, self.port)
        self.addCrackTaskToList(CrackTask)
        ttl = 5
        self.sendMasterResourceRequest(ttl, id)
        #TODO wait for some time to collect responses and divide the task between servant machines.
        pass

    def addCrackTaskToList(self, CrackTask):
        # TODO should be a function to add crackTasks as to update with received ones and
        # avoid something that might override the wrong way or duplicate.

        # TODO bonus for thinking: use datastructure for optimal result. (YAGNI?)

        #things to avoid: duplicate ids
            for
        pass

    def sendMasterResourceRequest(self, ttl, id):
        sendip = self.ip
        sendport = self.port
        for computer in self.computers:
            computer.sendResourceRequest(sendip, sendport, ttl, id, noask)
        #TODO implement sendResourceRequest(sendip, sendport, ttl, id, noask)

    def generateId(md5):
        #TODO generate a more unique md5 identificator
        return md5[1:5] + "420"

    def checkResourceAvailable(self):
        #TODO check if Server's resources are not allocated for some other task alredy.
        return True

    def parseRequestHeader(self, request_header):
        """
        method        GET
        path          '/resource?sendip=55.66.77.88&sendport=6788&ttl=5&id=wqeqwe23&noask=11.22.33.44_345&noask=111.222.333.444_223'
        version       'HTTP/1.1'

        command       '/resource'
        params        {'noask': ['11.22.33.44_345', '111.222.333.444_223'], 'sendip': ['55.66.77.88'], 'id': ['wqeqwe23'], 'sendport': ['6788'], 'ttl': ['5']}
        """
        lines = request_header.splitlines()
        first_line = lines[0]
        method, path, version = first_line.split()
        command, params = self.parsePath(path)
        return method, command, params

    def parsePath(self, path):
        q_data = urlparse(path)
        query = q_data.query
        return q_data.path, parse_qs(query)

    def close(self):
        pass


class CrackTask:
    def __init__(self, id, md5, masterIp, masterPort):
        self.md5 = md5
        self.id = id
        self.masterIp
        self.masterPort
        self.answer = None
        self.ranges = None
        self.wildcard = None



class Computer:
    def __init__(self, ip, port):
        """Form a new known computer

        Keyword arguments:
        ip -- computers ip
        port -- computers port
        """
        self.ip_address = ip
        self.port = port
        # Not important for slaves, Master deals with it
        self.resource_response = None
        self.task_to_solve = None
        self.work_response = None


    def prepareResourceRequestUrl(self):
        base_url = "http://%s:%s/resource" %(self.ip_address, self.port)
        params = {"sendip":"",
                  "sendport":"",
                  "ttl":"",
                  "noask":""}

        req = urllib2.Request(base_url)
        return req

    def sendCrackTask(self, CrackTask):
        pass

    def sendResourceRequest(self, ):
        url = None #TODO construct url
        response = urllib2.urlopen(url)
        print response.info()
        html = response.read()
        # do something
        response.close()  # best practice to close the file

    def __str__(self):
        return "my ip is: %s, port: %s" %(self.ip_address, self.port)

if(__name__== "__main__"):
    main()
