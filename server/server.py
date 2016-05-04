# Echo server program
import socket
import sys
import json
from run_search import search

#HOST = None              # Symbolic name meaning all available interfaces
HOST = 'localhost' # for testing
PORT = 20000
s = None

def establishConnection():
    for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, #IPv4/v6
                                  socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
        family, socktype, proto, canonname, sockaddr = res
        try:
            s = socket.socket(family, socktype, proto)
        except socket.error as msg:
            s = None
            continue
        try:
            s.bind(sockaddr)
            s.listen(1) # backlog, specifies max number of queued connections
        except socket.error as msg:
            s.close()
            s = None
            continue
        break
    if s is None:
        print 'could not open socket'
        sys.exit(1)
    conn, addr = s.accept()
    print 'Connected by', addr
    return conn,addr

def main():
    conn,addr = establishConnection()
    conn.send("Search for terms on wikipedia\n" +
              ".............................\n")
    while 1: # connected
        data = conn.recv(1024)
        if not data: break
        if data == "\n":
            print "."
            continue
        data = data.strip()
        if data.lower() == "q": break
        print 'Client is searching for "' + data + '"'
        sh = search(data)
        print "Sending results to client"
        conn.send(json.dumps(sh) + "\n")
    print "Terminating connection"
    conn.close()

if __name__ == '__main__':
    main()
