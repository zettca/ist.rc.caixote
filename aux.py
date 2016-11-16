import os
import time

ENC = "utf8"

def log(msg):
	print("[{}] {}".format(time.strftime("%H:%M:%S", time.localtime()), msg))

def readline_split(conn):
	byteses = b""
	while True:
		byte = conn.recv(1)
		if not byte or byte == b"\n": break
		byteses += byte
	return str(byteses, ENC).split(" ")

def make_line_bytes(lst):
	lst = [str(el) for el in lst]
	lst[-1] += "\n"
	return bytes(" ".join(lst), ENC)

def get_files(path):
	lst = []
	for path, dirs, files in os.walk(path):
		for fi in files:
			fpath = os.path.join(path, fi)
			stats = os.lstat(fpath)
			lst.append([int(stats.st_mtime), fpath])
	return lst

def send_file(conn, fpath):
	stats = os.lstat(fpath)
	with open(fpath, "rb") as fd:
		fbytes = fd.read()
	conn.sendall(make_line_bytes(["PUT", fpath, len(fbytes), int(stats.st_mtime)]))
	conn.sendall(fbytes)

def handle_file(s, fcode, fpath):
	if fcode == "SRVOLD":
		log("Uploading " + fpath)
		send_file(s, fpath)
		log("Uploaded " + fpath)
	elif fcode == "CLIOLD":
		s.sendall(make_line_bytes(["GET", fpath]))
		log("Requested " + fpath)
	else:
		log("but what is {}?".format(fcode))