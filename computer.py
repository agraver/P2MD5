import urllib2
import sys

def main():
    myMachine = Server(10000)
    myMachine.addComputersFromMachinesTxt()
    myMachine.boot()
    myMachine.listen()
    
class Server:
    def __init__(self, port):
        #initiate a localhost server
        self.ip = '127.0.0.1'
        self.port = port
        self.sock = None
        self.computers = []

    def addComputersFromMachinesTxt(self):
        try:
            f = open('machines.txt', 'r')
            # machines = f.read()
            machines = [["localhost", "10001"],["127.0.0.1", "10002"],["localhost", "10002"]]
            computers = [Computer(machine[0], machine[1]) for machine in machines]
            self.addComputers(computers)
        return None
            

    def addComputers(self, computers):
        """
        input:
            computers - list of Computer objects [Computer1, Computer2, ...]
        output:
            None
        """
        for computer in computers:
            if (computer not in self.computers):
                self.computers.append(computer)
        return None
        

    def boot(self, ip, port):
        self.address = (ip, port)
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
                data_string = ""
                while True:
                    data = connection.recv(22)
                    data_string += data
                    if not data:
                        break
                print >>sys.stderr, 'the whole data', data_string
                parse_result = self.parseDataString(data_string)
                if (parse_result == "resourceRequest"):
                    #TODO what to do in case of receiving a request about resource availability
                    pass
                elif (parse_result == "jobTask"):
                    #TODO what to do in case we receive a task to solve
                    pass
                else:
                    
            finally:
                # Clean up the connection
                connection.close()
            
        return None

    def parseDataString(data_string):
        #TODO try to parse it as a http header and determine what params
        

    def close(self):
        pass
        

class Computer:
    def __init__(self, ip, port):
        """Form a new known computer

        Keyword arguments:
        ip -- computers ip
        port -- computers port
        """
        self.ip = ip
        self.port = port
        # Not important for slaves, Master deals with it
        self.resource_response = None
        self.task_to_solve = None
        self.work_response = None 
        
    def __str__(self):
        return "my ip is: %s, port: %s" %(self.ip, self.port)

    def prepare_resource_request_url(self):
        base_url = "http://%s:%s/resource" %(self.ip, self.port)
        params = {"sendip":"",
                  "sendport":"",
                  "ttl":"",
                  "noask":""}
        
        req = urllib2.Request(base_url)
        return req

    def send_resource_request(self):
        
        response = urllib2.urlopen()
        print response.info()
        html = response.read()
        # do something
        response.close()  # best practice to close the file


if(__name__=="__main__"):
    main()
    
