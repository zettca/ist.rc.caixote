import _thread
import socket
import sys
import os
from srv_aux import *

HOST = "localhost"
PORT = int(sys.argv[1]) if len(sys.argv) > 1  else 50000
ROOT_PATH = "files"

logged_sockets = []

def client_thread_handler(sock):
	conn = sock["conn"]

	uaddr = "{}:{}".format(*sock["addr"])
	log("{} bound to thread...".format(uaddr))

	while True:
		# Get Header line, split by spaces
		headers = readline_split_utf8(conn)
		if not headers: # client exited early
			log("{} closed socket? :(".format(uaddr))
			global logged_sockets # V "logout" if logged in
			logged_sockets = [s for s in logged_sockets if s["addr"] != sock["addr"]]
			break

		# Get/Split header line
		method, header = headers[0], headers[1:]
		print(headers)

		if method == "LOG":
			sock["uname"], sock["upath"] = header
			uname, upath = sock["uname"], sock["upath"]
			filt = lambda s : s["uname"] == uname and s["upath"] == upath
			if not contains(logged_sockets, filt):
				logged_sockets.append(sock)
				log("{} logged in as {} to sync {}...".format(uaddr, uname, upath))
				conn.sendall(b"LOGGED PlsSendINF...\n")
			else:
				log("{} tried to double sync {}:{}. Already being synced...".format(uaddr, uname, upath))
				conn.sendall(b"ERRORE Alreadysyncingpath...\n")
				break
		elif method == "INF":
			lmtime, num_lines = header
			lines = []
			for i in range(int(num_lines)):
				lines.append(readline_split_utf8(conn))
				fpath, fmtime = lines[i][2], lines[i][1]
				filepath = os.path.join(ROOT_PATH, sock["uname"], lines[i][2])
				if os.path.exists(filepath):
					with os.lstat(filepath) as stats:
						if int(stats.st_mtime) > int(fmtime):
							print(filepath + "should be sent to client")
						elif int(stats.st_mtime) < int(fmtime):
							print(filepath + " outdated. pls send client!")
						else:
							print(filepath + " is up to date!")
				else:
					print(filepath + " does not exist. I should create it now, right?")
					print(filepath + " does not exist. client must send mee contents")


		elif method == "GET":
			print("not yet implemented.")
			conn.sendall("not yet implemented. sorry.")
		elif method == "PUT":
			print("not yet implemented.")
			conn.sendall("not yet implemented. sorry.")
		else:
			print("Method not valid. Not treated yet tho")

		#conn.sendall(b"(End of HEADER check)")

	log("Closing connection to {}:{}...".format(*addr))
	conn.close()

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
	_thread.start_new_thread(client_thread_handler, (sock,))

log("Server closing... but how ifnobreakonwhile?veryspookyindeed")
s.close()
