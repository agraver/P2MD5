from computer import Computer
from slaveComputer import SlaveComputer
from crackTask import CrackTask
import threading
import hashlib
import time

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

        # Send out /resourcereply only if we haven't done so yet
        if task_id not in server.resource_responded_task_ids:
            server.sendResourceReply(sendip, sendport, task_id, resource)
            server.resource_responded_task_ids.add(task_id)
        # TODO but remove the task_id from the set once we have tried to solve it
        # in order to be able to reply for resources
        # when another part from the same task is attempted to be solved again
        # say.. due to timeouts or unsolved tasks from slaves that died in the process.

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

        if task_id not in server.crack_tasks.keys():
            # we're getting a resourcereply to a CrackTask we haven't spawn
            pass

        crack_task = server.crack_tasks[task_id]

        if crack_task.locked:
            pass

        # a new computer instance for the given crackTask
        if computer_address not in crack_task.slave_computers.keys():
            # We create a MD5 computing slave_computer
            computer = Computer(ip, port)
            slave_computer = SlaveComputer(computer, resource)
            crack_task.addSlave(slave_computer)
            #update the crack_task object
            server.crack_tasks[task_id] = crack_task
        else:
            # we already received a response from this computer for this crackTask
            # if it's a repeated calculation, the program shouldn't
            # get here, since it would reply the answer right away and not ask for resources
            pass


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

        # while calculating set the server's resource as unavailable
        server.resource['available'] = False
        print "Slave is now busy calculating..."

        self.timeout = 30
        print "solver timeout is set to %i" %(self.timeout)
        self.start_time = time.time()
        result = 1 # not found code

        failed_templates = []

        for template in ranges:
            status, result_string = self.md5solver(md5, template, wildcard)

            if status == 0:
                print("cracking "+ md5 +" with template" + template + " gave " + result_string)
                break
            elif status == 1:
                print("failed to crack " + md5 + " with template " + template)
                failed_templates.append(template)
                continue
            elif status == 2:
                print "solver timed out"
                break

        # TODO pass failed templates along with the answer for possible recalculation
        server.sendMd5Answer(master_ip, master_port, task_id, md5, status, result_string, failed_templates)
        print "Answer for the resulting cracking attempt has been sent out"
        server.resource_responded_task_ids.discard(task_id)
        print "the task_id is removed from resource_responded_task_ids"
        server.resource['available'] = True
        print "Slave is once again ready for work"


    def md5solver(self, hexhash, template, wildcard):
        # instantiate template and crack all instatiations
        # first block recursively instantiates template
        i = 0
        found = False
        while i < len(template):
            if template[i] == wildcard:
                found = True
                char = 32 # start with this char ascii
                while char < 126:
                    c = chr(char)
                    if c != wildcard: # cannot check wildcard!

                        ntemplate = template[:i] + c + template[i+1:]
                        status, result_string = self.md5solver(hexhash, ntemplate, wildcard)

                        if status in [0,2]:
                            return status, result_string

                    char += 1
            i += 1

        # timeout scenario
        if (time.time() - self.start_time > self.timeout):
            return 2, None

        # instantiation loop done
        if not found:
            # no wildcards found in template: crack
            m = hashlib.md5()
            m.update(template)
            h4sh = m.hexdigest() # hash is a built-in function name
            #print("template: "+template+" hash: "+h4sh)
            if h4sh == hexhash:
                return 0, template # cracked!
        return 1, None

    def answermd5(self, server, params):
        # answermd5:[ip, port, id, md5, result, resultstring]
        # what should the Master Server do once it receives replies about crack?
        # print out the result
        from_ip = params['ip']
        from_port = str(params['port'])
        task_id = params['id']
        md5 = params['md5']
        result = params['result']
        resultstring = params['resultstring']
        failed_templates = params['failed_templates']
        from_address = '%s_%s' %(from_ip, from_port)

        if task_id not in server.crack_tasks.keys():
            # we're getting an answer to a CrackTask we haven't spawn
            pass

        crack_task = server.crack_tasks[task_id]
        crack_task.answered_computers.add(from_address)

        if result == 0:
            print "Master is processing the Result Found case"
            crack_task.solved = True
            crack_task.answer = resultstring
            print "next I'm sending the resultstring to server.connection"
            response = '<p> Result of the calculation is: %s\n' %(resultstring)
            server.connection.send(response)
            server.connection.send('</body></html>\n\n')
            print "closing server.connection"
            server.connection.close()
            server.connection = None
            return

        elif result == 1:
            print "Master is processing the Result Not Found case"
            # Add ranges to the ones that have already been looked through
            crack_task.failed_templates += crack_task.divided_ranges[from_address]

        elif result == 2:
            print "Master is processing the Timed Out case"
            crack_task.failed_templates += failed_templates
            # Think about this one...

        def recalculate():
            print "######################"
            print "######################"
            print "######################"
            print "######################"
            print "######################"
            print "######################"
            print "I am the recalculator"
            print crack_task.failed_templates
            #reset time in crackTask
            crack_task.startTime = time.time()
            crack_task.locked = False
            #reset crackTask's slave omputers
            crack_task.slave_computers = {}
            crack_task.answered_computers = set()
            #send new resource queries
            server.sendMasterResourceRequest(5, crack_task.task_id)
            print "self.sendMasterResourceRequest(ttl, task_id) successful"

            t = threading.Timer(5, server.printCrackTask, args=(task_id,))
            t.start()
            t.join() # wait until finished

            crack_task.locked = True

            server.masterCrackTaskProcess(crack_task)

            return

        if crack_task.everyoneResponded() or crack_task.timedOut():
            if not crack_task.solved:
                recalculate()

    def crack(self, server, params):
        md5 = params["md5"][0]

        crack_task = CrackTask(server.myselfAsComputer, md5)
        task_id = crack_task.task_id

        if task_id in server.crack_tasks.keys():
            crack_task = server.crack_tasks[task_id]
            if crack_task.solved:
                # Give the answer right away
                print "the task is already solved"
                resultstring = crack_task.answer
                response = '<p> Oh! I already have the answer. It is: %s\n' %(resultstring)
                server.connection.send(response)
                server.connection.send('</body></html>\n\n')
                print "closing server.connection"
                server.connection.close()
                server.connection = None
                return
            else:
                print "the task is in the process of being solved"
                response = '<p> this md5 is currently being solved, try to refresh the page again later for results\n'
                server.connection.send(response)
                server.connection.send('</body></html>\n\n')
                print "closing server.connection"
                server.connection.close()
                server.connection = None
                return

        server.crack_tasks[task_id] = crack_task

        ttl = 5
        server.sendMasterResourceRequest(ttl, task_id)
        print "self.sendMasterResourceRequest(ttl, task_id) successful"

        t = threading.Timer(5, server.printCrackTask, args=(task_id,))
        t.start()
        t.join() # wait until finished

        crack_task.locked = True

        t = threading.Thread(target=server.masterCrackTaskProcess, args=(crack_task,))
        t.start()
