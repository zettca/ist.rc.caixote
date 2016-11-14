import socket
import stat
import sys
import os
from aux import *

if len(sys.argv) < 5:
	print("USAGE: Caixote.py HOST PORT USERNAME DIRECTORY")
	sys.exit(-1)

HOST = sys.argv[1]
PORT = int(sys.argv[2])
USER = sys.argv[3]
DIR = sys.argv[4]
ENC = "utf8"

def put_files(path, lst):
	for f in os.listdir(path): 	# List files
		fp = os.path.join(path, f)
		stats = os.lstat(fp)

		if stat.S_ISREG(stats.st_mode):
			lst.append(["-", int(stats.st_mtime), fp[fp.find("/")+1:]])
		elif stat.S_ISDIR(stats.st_mode):
			lst.append(["d", int(stats.st_mtime), fp[fp.find("/")+1:]])
			put_files(fp, lst)
		else:
			print(f + " has a weird filetype. skipping...")

# ========== MAIN ========== #

'''
for path, dirs, files in os.walk(DIR):
	print((path, files))

filelist = []
put_files(DIR, filelist)
filelist = sorted(filelist, key=lambda el : el[0], reverse=True)

for el in filelist:
	print(el)
'''

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	s.connect((HOST, PORT))
except socket.error as err:
	print(err)
	s.connect((HOST, PORT+1))
	print("Bound on next port({})".format(PORT+1)) 

# Login to server
s.sendall(make_line_bytes(["LOG", USER, DIR]))
print("SENT LOG request...")

while True:
	data = readline_split_utf8(s)
	if not data:
		print("Server closed connection. :(")
		break

	print(data)
	code, desc = data

	if code=="LOGGED": # Login Successful. Send INF (FilesInfo)
		print("I logged, nice!")
		header, files = [], []
		put_files(DIR, files)
		files = sorted(files, key=lambda el : el[2].count("/"))

		lmtime = files[0][0]
		header = make_line_bytes(["INF", lmtime, len(files)])
		s.send(header)
		
		for file in files:
			print(file)
			s.send(make_line_bytes(file))
		print("Sent INF request...")

	elif code=="ERRORE":
		print("Shit. Couldn't h4ck")
	else:
		print("WTF does {} mean?".format(code))

s.close()
