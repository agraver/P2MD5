from Server import Server

def main():
    #TODO how to undbind the sockets?
    my_machine = Server(10007)
    my_machine.addComputersFromMachinesTxt()
    my_machine.boot()
    my_machine.listen() #should decide what to do with incoming GET/POST requests

if(__name__== "__main__"):
    main()
