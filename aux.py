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

def send_file(conn, fpath):
	stats = os.lstat(fpath)
	with open(fpath, "rb") as fd:
		fbytes = fd.read()
	conn.sendall(make_line_bytes(["PUT", fpath, len(fbytes), int(stats.st_mtime)]))
	conn.sendall(fbytes)

def request_file_diff(conn, dir):
	flist = []
	for path, dirs, files in os.walk(dir):
		for fi in files:
			fpath = os.path.join(path, fi)
			stats = os.lstat(fpath)
			flist.append([int(stats.st_mtime), fpath])

	conn.sendall(make_line_bytes(["DIFF", len(flist)]))
	for file in flist:
		conn.sendall(make_line_bytes(file))