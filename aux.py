import os

ENC = "utf8"

def readline_split(conn):
	byteses = conn.recv(1)
	if not byteses:	return None
	while True:
		byte = conn.recv(1)
		if byte != b"\n":
			byteses += byte
		else:
			break
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
