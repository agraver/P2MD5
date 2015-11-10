from server import Server
import sys

def main():

    if len(sys.argv) == 2:
        machine = Server(int(sys.argv[1]))
        machine.addComputersFromMachinesTxt()
        machine.boot()
        machine.listen()
        # Master send resource request
    else:
        print "This program is used: main.py <port> (<master>)"


if __name__== "__main__":
    main()
