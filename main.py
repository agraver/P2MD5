from server import Server
import sys

def main():

    arg_count = len(sys.argv)

    if arg_count in [2, 3]:
        machine = Server(int(sys.argv[1]))
        machine.addComputersFromMachinesTxt()
        machine.boot()
        if arg_count == 3 and sys.argv[2].lower() == 'master':
            machine.startCracking("lambi")
        else:
            machine.listen()

    else:
        print "This program is used: main.py <port> (<master>)"


if __name__== "__main__":
    main()
