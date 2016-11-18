import socket
import sys
from _thread import start_new_thread
from srv_aux import client_handler, log

if len(sys.argv) < 2:
	print("USAGE: python Server.py PORT")
	sys.exit(-1)

HOST, PORT = "", int(sys.argv[1])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(64)

log("Server listening on port {}...".format(PORT))

while True:
	conn, addr = s.accept()
	log("{}:{} connected".format(*addr))
	sock = {"addr": addr, "conn": conn}
	try:
		start_new_thread(client_handler, (sock,))
	except Exception as e:
		log("Exception with {}:{} | {}".format(addr[0], addr[1], e))
