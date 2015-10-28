from urlparse import urlparse, parse_qs

def main():
    s = "/resource?sendip=55.66.77.88&sendport=6788&ttl=5&id=wqeqwe23&noask=11.22.33.44_345&noask=111.222.333.444_223"
    print urlparse(s)
    query = urlparse(s).query
    print parse_qs(query)


if __name__ == "__main__":
    main()
