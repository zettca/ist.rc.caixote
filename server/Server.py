import socket
import sys
from _thread import start_new_thread
from srv_aux import log, client_thread_handler

if len(sys.argv) < 2:
	print("USAGE: python Server.py PORT")
	sys.exit(-1)

HOST, PORT = "localhost", int(sys.argv[1])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((HOST, PORT))
s.listen()

while True:
	conn, addr = s.accept()
	log("{}:{} connected".format(addr[0], addr[1]))
	sock = {"addr": addr, "conn": conn}
	start_new_thread(client_thread_handler, (sock,))

s.close()
