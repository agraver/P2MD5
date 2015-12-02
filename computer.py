import json, urllib, urllib2

class Computer(object):
    def __init__(self, ip_address, port):
        """Form a new known computer

        Keyword arguments:
        ip -- computers ip
        port -- computers port
        """
        self.ip_address = ip_address
        self.port = port

    def sendTask(self, master_ip, master_port, task_id, md5, ranges, wildcard, symbolrange):
        url = "http://%s:%s/checkmd5" %(self.ip_address, self.port)
        params = {"ip": master_ip, "port": master_port,\
                "id": task_id, "md5": md5, "ranges": ranges,\
                "wildcard": wildcard, "symbolrange": symbolrange}
        data = json.dumps(params)
        req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        response_stream = urllib2.urlopen(req, timeout=1)
        response_stream.close()

    def prepareResourceRequestUrl(self, sendip, sendport, ttl, task_id, noask):
        base_url = "http://%s:%s/resource" %(self.ip_address, self.port)
        params = {"sendip":sendip, "sendport":sendport, "ttl":ttl, "id":task_id, "noask":noask}
        url_params = urllib.urlencode(params, True)
        url = base_url + "?" + url_params
        return url

    def sendResourceRequest(self, sendip, sendport, ttl, task_id, noask):
        url = self.prepareResourceRequestUrl(sendip, sendport, ttl, task_id, noask)
        print url
        #print "i get stuck here"
        try:
            response = urllib2.urlopen(url, timeout=1)
        except urllib2.URLError, e:
            raise
        except:
            raise

        print "urlopen() successful"
        response.close()  # best practice to close the file
        print "response.close() successful"

    def __str__(self):
        return "my ip is: %s, port: %s" %(self.ip_address, self.port)
