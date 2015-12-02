from server import Server
import sys

def main():

    arg_count = len(sys.argv)

    if arg_count == 2:
        machine = Server(int(sys.argv[1]))
        machine.boot()
        machine.listen()

    else:
        print "Usage: python main.py <port>"


if __name__== "__main__":
    main()
