from server import Server

def main():
    machine = Server(10007)
    machine.addComputersFromMachinesTxt()
    machine.boot()
    machine.listen()

if __name__== "__main__":
    main()
