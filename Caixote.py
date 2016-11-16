import socket
import sys
from aux import *

if len(sys.argv) < 5:
	print("USAGE: python Caixote.py HOST PORT USERNAME DIRECTORY")
	sys.exit(-1)

HOST, PORT, USER, DIR = sys.argv[1:5]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, int(PORT)))
print("Connected to server at {}:{} ".format(HOST, PORT))

s.sendall(make_line_bytes(["LOG", USER, DIR])) # Login request

while True:
	data = readline_split(s)
	if not data:
		print("Server closed connection. :(")
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
			print("Directory is already synchronized. Exiting...")
			break

		for _ in range(files):
			fcode, fpath = readline_split(s)
			if fcode == "SRVOLD":
				print("Uploading " + fpath)
				send_file(s, fpath)
				print("Uploaded " + fpath)
			elif fcode == "CLIOLD":
				s.sendall(make_line_bytes(["GET", fpath]))
				print("Requested " + fpath)
			else:
				print("but what is {}?".format(fcode))

		# Client done with requests. Can exit
		#print("Sent/Received all files successfully Exiting...")
		#break

	elif code == "TOSAVE":
		fpath, flength, fmtime = headers
		flength = int(flength)
		fbytes = s.recv(flength)
		while len(fbytes) < flength: # sometimes recv doesn't receive all bytes
			add_bytes = s.recv(flength - len(fbytes))
			fbytes += add_bytes # additional bytes
			print("Downloading {} [{}/{} {}%]".format(fpath, len(fbytes), flength, int(100*len(fbytes)/flength)))

		os.makedirs(os.path.split(fpath)[0], exist_ok=True)
		with open(fpath, "wb") as fd:
			fd.write(fbytes)
			fd.close()
		os.utime(fpath, (int(fmtime), int(fmtime)))
		print("Downloaded " + fpath)

	elif code == "GOAWAY":
		print("Server refused connection... Already Logged somewhere else")

	elif code:
		print("Unknown code: {}".format(code))

	else:
		print("All synced? Killing myself.")
		break

print("Closing connection to server...")
s.close()
