import time

def readline_split_utf8(conn):
	byteses = conn.recv(1)
	if not byteses: return None
	while True:
		byte = conn.recv(1)
		if byte != b"\n":
			byteses += byte
		else:
			break
	return str(byteses, "utf8").split(" ")

def log(msg):
	print("[{}] {}".format(time.strftime("%H:%M:%S", time.localtime()), msg))

def contains(lst, filter):
	for el in lst:
		if filter(el):
			return True
	return False
