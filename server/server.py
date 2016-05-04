# Echo server program
import socket
import sys

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
    while 1: # connected
        data = conn.recv(1024)
        if not data: break
        call("")
        print data
        conn.send(data)
    conn.close()

if __name__ == '__main__':
    main()
