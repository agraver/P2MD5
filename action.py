from computer import Computer
from slaveComputer import SlaveComputer
from crackTask import CrackTask
import hashlib

class Action():

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

    def resource(self, server, params):
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

        #TODO Build further check resource logic.
        if server.checkResourceAvailable():
            resource = server.getResourceAmount()
        else:
            resource = 0

        print "sendip:", sendip, "sendport:", sendport, "task_id:", task_id, "resource:", resource

        # Send out /resourcereply only if we haven't done so in the past
        if task_id not in server.responded_task_ids:
            server.sendResourceReply(sendip, sendport, task_id, resource)
            server.responded_task_ids.add(task_id)

        # Next step would be sending out requests to all the machines
        # that I, myself, as a Server, know from "machines.txt" file.
        if ttl > 0:
            print "Sending out requests to minions"
            server.sendResourceRequestToOthers(task_id, sendip, sendport, ttl, noask)
        else:
            print "ttl has been exhausted. Resource request distribution has been terminated"

    def resourcereply(self, server, params):
        ip = params['ip']
        resource = params['resource']
        port = str(params['port'])
        task_id = params['id']
        computer_address = "%s_%s" % (ip, port)

        # If this is a new computer instance to us.
        if computer_address not in server.responded_computers:
            # We create a MD5 computing slave_computer
            computer = Computer(ip, port)
            slave_computer = SlaveComputer(computer, resource)

            if task_id not in server.crack_tasks.keys():
                pass

            crack_task = server.crack_tasks[task_id]
            crack_task.addSlave(slave_computer)
            #update the crack_task object
            server.crack_tasks[task_id] = crack_task
            #print crack_task


    def checkmd5(self, server, params):
        print "inside checkmd5()"
        master_ip = params['ip']
        master_port = str(params['port'])
        task_id = params['id']
        md5 = params['md5']
        ranges = params['ranges']
        try:
            wildcard = params['wildcard']
        except:
            wildcard = "?"
        try:
            symbolrange = params['symbolrange']
        except:
            symbolrange = [[32,126]]

        print "params initiated as variables"
        for template in ranges:
            result = self.md5solver(md5, template, wildcard)
            if result:
                print("cracking "+ md5 +" with template" + template + " gave " + result)
            else:
                print("failed to crack " + md5 + " with template " + template)

    def md5solver(self, hexhash, template, wildcard):
        #"instantiate template and crack all instatiations"
        # first block recursively instantiates template
        i=0
        found=False
        while i<len(template):
            if template[i]==wildcard:
                found=True
                char=32 # start with this char ascii
                while char<126:
                    c=chr(char)
                    if c!=wildcard: # cannot check wildcard!
                        ntemplate=template[:i]+c+template[i+1:]
                        print("i: "+str(i)+" ntemplate: "+ntemplate)
                        res=self.md5solver(hexhash,ntemplate, wildcard)
                        if res: # stop immediately if cracked
                            return res
                    char+=1
            i+=1
        # instantiation loop done
        if not found:
            # no wildcards found in template: crack
            m = hashlib.md5()
            m.update(template)
            h4sh = m.hexdigest()
            #print("template: "+template+" hash: "+hash)
            if h4sh == hexhash:
                return template # cracked!
        # template contains wildcards
        return None

    def answermd5(self, server, params):
        pass

    def crack(self, server, params):
        server.startCracking(params["md5"][0])
