import socket
import sys
from aux import *

if len(sys.argv) < 5:
	print("USAGE: python Caixote.py HOST PORT USERNAME DIRECTORY")
	sys.exit(-1)

HOST, PORT, USER, DIR = sys.argv[1:5]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, int(PORT)))
log("Connected to server at {}:{} ".format(HOST, PORT))

s.sendall(make_line_bytes(["LOG", USER, DIR])) # Login request

while True:
	data = readline_split(s)
	if not data:
		log("Server closed connection. :(")
		break

	#print(data)
	code, headers = data[0], data[1:]

	if code == "LOGGED": # Login Successful.
		files = sorted(get_files(DIR), key=lambda el : el[1].count("/"))
		s.sendall(make_line_bytes(["INF", len(files)]))
		for file in files:
			s.sendall(make_line_bytes(file))
	
	elif code == "TOSYNC":
		files = int(headers[0])
		if files == 0: # nothing to sync
			log("Directory is already synchronized. Exiting...")
			break

		for _ in range(files):
			fcode, fpath = readline_split(s)
			handle_file(s, fcode, fpath)

		# Client done with requests. Can exit
		#log("Sent/Received all files successfully Exiting...")
		#break

	elif code == "TOSAVE":
		fpath, flength, fmtime = headers
		flength = int(flength)
		fbytes = s.recv(flength)
		while len(fbytes) < flength: # sometimes recv doesn't receive all bytes
			add_bytes = s.recv(flength - len(fbytes))
			fbytes += add_bytes # additional bytes
			log("Downloading {} [{}/{} {}%]".format(fpath, len(fbytes), flength, int(100*len(fbytes)/flength)))

		os.makedirs(os.path.split(fpath)[0], exist_ok=True)
		with open(fpath, "wb") as fd:
			fd.write(fbytes)
			fd.close()
		os.utime(fpath, (int(fmtime), int(fmtime)))
		log("Downloaded " + fpath)

	elif code == "GOAWAY":
		log("Server refused connection... Already Logged somewhere else")

	elif code:
		log("Unknown code: {}".format(code))

	else:
		log("All synced? Killing myself.")
		break

log("Closing connection to server...")
s.close()
