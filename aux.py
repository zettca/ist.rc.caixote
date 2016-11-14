ENC = "utf8"

def readline_split_utf8(conn):
	byteses = conn.recv(1)
	if not byteses:	return None
	while True:
		byte = conn.recv(1)
		if byte != b"\n":
			byteses += byte
		else:
			break
	return str(byteses, ENC).split(" ")

def make_line(tup):
	lst = [str(el) for el in tup]
	lst[-1] += "\n"
	return " ".join(lst)

def make_line_bytes(tup):
	return bytes(make_line(tup), ENC)
