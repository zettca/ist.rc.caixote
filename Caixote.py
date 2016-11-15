import socket
import sys
from aux import *

if len(sys.argv) < 5:
	print("USAGE: python Caixote.py HOST PORT USERNAME DIRECTORY")
	sys.exit(-1)

HOST, PORT, USER, DIR = sys.argv[1:5]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, int(PORT)))

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
			print("ALL FILES ARE SYNCED! WEE! EXITING")
			break

		for _ in range(files):
			fcode, fpath = readline_split(s)
			if fcode == "SRVOLD":
				stats = os.lstat(fpath)
				fown, fmtime = stats.st_uid, stats.st_mtime
				with open(fpath, "rb") as fd:
					fbytes = fd.read()
					fd.close()
				s.sendall(make_line_bytes(["PUT", fpath, len(fbytes), fown, int(fmtime)]))
				sentbytes = s.send(fbytes)
				if sentbytes < len(fbytes):
					print("Error uploading " + fpath)
				else:
					print("Successfully uploaded " + fpath)
			elif fcode == "CLIOLD":
				s.sendall(make_line_bytes(["GET", fpath]))
				print("Requesting " + fpath)
			else:
				print("but what is {}?".format(fcode))

	elif code == "TOSAVE":
		fpath, flength, fown, fmtime = headers
		fbytes = s.recv(int(flength))
		os.makedirs(os.path.split(fpath)[0], exist_ok=True)
		with open(fpath, "wb") as fd:
			fd.write(fbytes)
			fd.close()
		os.utime(fpath, (int(fmtime), int(fmtime)))
		os.chown(fpath, int(fown), int(fown))
		print("Successfully downloaded " + fpath)

	elif code == "GOAWAY":
		print("Server refused connection...")

	elif code:
		print("Unknown code: {}".format(code))

	else:
		print("All synced? Kill myself?")

print("Closing connection to server...")
s.close()
