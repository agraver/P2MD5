import urllib, urllib2

class Computer:
    def __init__(self, ip_address, port):
        """Form a new known computer

        Keyword arguments:
        ip -- computers ip
        port -- computers port
        """
        self.ip_address = ip_address
        self.port = port
        # Not important for slaves, Master deals with it
        self.resource_response = None ## arvut
        self.task_to_solve = None ## tulevikuks
        self.work_response = None ## tulevikuks


    def prepareResourceRequestUrl(self, sendip, sendport, ttl, task_id, noask):
        base_url = "http://%s:%s/resource" %(self.ip_address, self.port)
        params = {"sendip":sendip, "sendport":sendport, "ttl":ttl, "id":task_id, "noask":noask}
        url_params = urllib.urlencode(params, True)
        url = base_url + "?" + url_params
        return url

    def sendCrackTask(self, CrackTask):
        pass

    def sendResourceRequest(self, sendip, sendport, ttl, task_id, noask):
        url = self.prepareResourceRequestUrl(sendip, sendport, ttl, task_id, noask)
        print url
        response = urllib2.urlopen(url)
        print response.info()
        html = response.read()
        print html
        # do something
        response.close()  # best practice to close the file

    def __str__(self):
        return "my ip is: %s, port: %s" %(self.ip_address, self.port)
