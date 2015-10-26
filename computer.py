import urllib2
import socket
import sys

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
        self.computers = []

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
                data_string = ""
                while True:
                    data = connection.recv(32)
                    print data
                    if data:
                        data_string += data
                        connection.sendall(data)
                    else:
                        print "No more data"
                        break

                # print >>sys.stderr, 'the whole data', data_string
                parse_result = self.parseDataString(data_string)
                print "I got behind the parsing thingy!"
                if parse_result == "resourceRequest":
                    #TODO what to do in case of receiving a request about resource availability
                    pass
                elif (parse_result == "jobTask"):
                    #TODO what to do in case we receive a task to solve
                    pass
            except:
                print >>sys.stderr, "An error has occured while listening."

            finally:
                # Clean up the connection
                print "I closed the connection, yeeah."
                connection.close()

        return None

    def parseDataString(self, data_string):
        #TODO try to parse it as a http header and determine what params
        return "Parsed Data String (http header)"

    def close(self):
        pass


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

    def __str__(self):
        return "my ip is: %s, port: %s" %(self.ip_address, self.port)

    def prepare_resource_request_url(self):
        base_url = "http://%s:%s/resource" %(self.ip_address, self.port)
        params = {"sendip":"",
                  "sendport":"",
                  "ttl":"",
                  "noask":""}

        req = urllib2.Request(base_url)
        return req

    def send_resource_request(self):
        url = None #TODO construct url
        response = urllib2.urlopen(url)
        print response.info()
        html = response.read()
        # do something
        response.close()  # best practice to close the file


if(__name__== "__main__"):
    main()
