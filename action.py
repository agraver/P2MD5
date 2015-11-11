from computer import Computer
from slaveComputer import SlaveComputer
from crackTask import CrackTask

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
            # If we already have a crack_task with this id.
            crack_task = CrackTask(task_id)
            if task_id in server.crack_tasks.keys():
                crack_task = server.crack_tasks[task_id]
            print crack_task.__str__()
            crack_task.addSlave(slave_computer)
            print crack_task.__str__()
            server.crack_tasks[task_id] = crack_task


    def checkmd5(self, server, params):
        pass

    def answermd5(self, server, params):
        pass

    def crack(self, server, params):
        server.startCracking(params["md5"])
