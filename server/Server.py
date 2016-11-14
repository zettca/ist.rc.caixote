import socket
import sys
from _thread import start_new_thread
from srv_aux import *

if len(sys.argv) < 2:
	print("USAGE: Server.py PORT")
	sys.exit(-1)

HOST = "localhost"
PORT = int(sys.argv[1])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	s.bind((HOST, PORT))
except socket.error as err:
	log(err)
	s.bind((HOST, PORT+1))
	log("Bound on next port({})".format(PORT+1))

s.listen()
log("Listening for clients...")

while True:
	(conn, addr) = s.accept() # returns tuple
	log("{}:{} connected".format(addr[0], addr[1]))
	sock = {"addr": addr, "conn": conn}
	start_new_thread(client_thread_handler, (sock,))

log("Server closing... but how? ifnotbreakableonwhile?veryspookyindeed")
s.close()
