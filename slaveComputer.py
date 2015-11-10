from computer import Computer

class SlaveComputer (Computer):
    def  __init__(self, computer, resource_response):
        ip = computer.ip_address
        port = computer.port
        Computer.__init__(self, ip, port)
        self.resource_response = resource_response
        self.task_to_solve = None
        self.work_response = None

    def __str__(self):
        ip = self.ip_address
        port = self.port
        resource = self.resource_response
        return "My slavian address: %s_%s. I have %s resource" %(ip, port, resource)
