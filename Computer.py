
import urllib2
from CrackTask import *

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
