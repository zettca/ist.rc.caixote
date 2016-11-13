import socket
import stat
import sys
import os
from hashlib import md5
from cli_aux import *

if len(sys.argv) < 5:
	print("USAGE: Caixote HOST PORT USERNAME DIRECTORY")
	sys.exit(-1)

HOST = sys.argv[1]
PORT = int(sys.argv[2])
USER = sys.argv[3]
DIR = sys.argv[4]
ENC = "utf8"

def put_files(path, lst):
	for f in os.listdir(path): 	# List files
		filepath = os.path.join(path, f)
		stats = os.lstat(filepath)

		if stat.S_ISREG(stats.st_mode):
			with open(filepath, 'rb') as fd:
				checksum = md5(fd.read()).hexdigest() # hash for stuffs?
			lst.append((int(stats.st_mtime), stats.st_uid, filepath, checksum))
		elif stat.S_ISDIR(stats.st_mode):
			#lst.append(("d", int(stats.st_mtime), stats.st_uid, filepath))
			put_files(filepath, lst)
		else:
			print(f + " has a weird filetype. skipping...")

# ========== MAIN ========== #

filelist = []
put_files(DIR, filelist)
filelist = sorted(filelist, key=lambda el : el[3], reverse=True)

for el in filelist:
	print(el)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	s.connect((HOST, PORT))
except socket.error as err:
	print(err)
	s.connect((HOST, PORT+1))
	print("Bound on next port({})".format(PORT+1)) 

# Login to server
header = " ".join(["LOG", USER, DIR+"\n"])
s.sendall(bytes(header, ENC))
print("Attempted to login. Ready to recv from server...")

while True:
	data = readline_split_utf8(s)
	print(data)
	code, desc = data
	if not data:
		print("Server closed connection. :(")
		break

	if code=="LOGGED":
		print("I logged, nice!")
	elif code=="ERRORE":
		print("Shit. Couldn't h4ck")
	else:
		print("WTF does {} mean?".format(code))

s.close()