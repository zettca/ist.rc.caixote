import socket
import sys
from aux import *

if len(sys.argv) < 5:
	print("USAGE: python Caixote.py HOST PORT USERNAME DIRECTORY")
	sys.exit(-1)

HOST, PORT, USER, DIR = sys.argv[1:5]
all_files_downloaded, all_files_uploaded = False, False

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, int(PORT)))
log("Connected to server at {}:{} ".format(HOST, PORT))

s.sendall(make_line_bytes(["LOG", USER, DIR])) # Login request

while True:
	if all_files_uploaded and all_files_downloaded:
		log("Directory successfully synchronized. Exiting...")
		break

	data = readline_split(s) # waits for a line to be sent
	if not data:
		log("Server closed connection. :(")
		break

	#print(data)
	code, headers = data[0], data[1:]

	if code == "LOGGED": # Login Successful.
		request_file_infos(s, DIR)
	
	elif code == "TOSYNC":
		num_files = int(headers[0])
		if num_files == 0: # nothing to sync
			log("Directory is already synchronized. Exiting...")
			break

		my_olds = []
		for _ in range(num_files): # upload/request all files needed
			fcode, fpath = readline_split(s)
			if fcode == "SRVOLD":
				log("Uploading " + fpath)
				send_file(s, fpath)
				log("Uploaded " + fpath)
			elif fcode == "CLIOLD":
				log("Requesting " + fpath)
				my_olds.append(fpath)
			else:
				log("but what is {}?".format(fcode))

		all_files_uploaded = True
		if my_olds:
			s.sendall(make_line_bytes(["GEN", len(my_olds)]))
			body = b""
			for line in my_olds:
				body += make_line_bytes([line])
			s.sendall(body)
		else:
			all_files_downloaded = True

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
