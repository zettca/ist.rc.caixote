import time
import os

ENC = "utf8"
ROOT_PATH = "files"
logged_sockets = []

def log(msg):
	print("[{}] {}".format(time.strftime("%H:%M:%S", time.localtime()), msg))

def readline_split(conn):
	byteses = conn.recv(1)
	if not byteses:	return None
	while True:
		byte = conn.recv(1)
		if byte == b"\n": break
		byteses += byte
	return str(byteses, ENC).split(" ")

def make_line_bytes(lst):
	lst = [str(el) for el in lst]
	lst[-1] += "\n"
	return bytes(" ".join(lst), ENC)

def contains(lst, filter):
	for el in lst:
		if filter(el):
			return True
	return False

def get_files_clirelative(path):
	lst = []
	for path, dirs, files in os.walk(path):
		ppath = "/".join(path.split("/")[2:])
		for fi in files:
			lst.append(os.path.join(ppath, fi))
	return lst

# ==================== #

def handle_info_request(sock, headers):
	num_lines = headers[0]
	urpath = os.path.join(ROOT_PATH, sock["uname"], sock["upath"])
	os.makedirs(urpath, exist_ok=True)

	cli_files, srv_files = [], get_files_clirelative(urpath)
	response = []

	for _ in range(int(num_lines)):
		line = readline_split(sock["conn"])
		cf_mtime, cf_path = int(line[0]), line[1]
		sf_path = os.path.join(ROOT_PATH, sock["uname"], cf_path)
		cli_files.append(cf_path)

		if not os.path.exists(sf_path): # File doesn't exist
			response.append(["SRVOLD", cf_path])
		elif os.path.isfile(sf_path):
			st = os.lstat(sf_path)
			if int(st.st_mtime) > cf_mtime:
				response.append(["CLIOLD", cf_path])
			elif int(st.st_mtime) < cf_mtime:
				response.append(["SRVOLD", cf_path])

	for fi in set(srv_files) - set(cli_files): # New file to client
		response.append(["CLIOLD", fi])

	return response

def client_handler(sock):
	conn, addr = sock["conn"], sock["addr"]
	log("{}:{} bound to thread".format(*addr))

	while True:
		head = readline_split(conn) # Get Header line, split by spaces
		if not head:
			log("{}:{} closed socket? :(".format(*addr))
			global logged_sockets # V "logout" if logged in
			logged_sockets = [s for s in logged_sockets if s["addr"] != addr]
			break

		#print(head)
		method, headers = head[0], head[1:] # Split header line

		if method == "LOG": # CLIENT REQUESTED "LOGIN" 
			uname, upath = headers
			sock["uname"], sock["upath"] = uname, upath
			filt = lambda s : s["uname"] == uname and s["upath"] == upath
			if not contains(logged_sockets, filt):
				logged_sockets.append(sock)
				conn.sendall(b"LOGGED arg2\n")
			else:
				conn.sendall(b"ERRORE arg2\n")
				break

		elif method == "INF": # CLIENT REQUESTED FILES INFOS
			response = handle_info_request(sock, headers)
			conn.sendall(make_line_bytes(["TOSYNC", len(response)]))
			for line in response:
				print(line)
				conn.sendall(make_line_bytes(line))

		elif method == "GET": # CLIENT REQUESTED FILE CONTENTS
			fpath = headers[0]
			sf_path = os.path.join(ROOT_PATH, sock["uname"], fpath)
			stats = os.lstat(sf_path)
			fown, fmtime = stats.st_uid, stats.st_mtime
			with open(sf_path, "rb") as fd:
				fbytes = fd.read()
				fd.close()
			conn.sendall(make_line_bytes(["TOSAVE", fpath, len(fbytes), fown, int(fmtime)]))
			conn.sendall(fbytes)
			log("Successfully uploaded " + fpath)

		elif method == "PUT": # CLIENT SENT FILES CONTENTS 
			fpath, flength, fown, fmtime = headers
			print("file has" + int(flength))
			fbytes = conn.recv(int(flength))
			sf_path = os.path.join(ROOT_PATH, sock["uname"], fpath)
			os.makedirs(os.path.split(sf_path)[0], exist_ok=True)
			with open(sf_path, "wb") as fd:
				fd.write(fbytes)
				fd.close()
			os.utime(sf_path, (int(fmtime), int(fmtime)))
			os.chown(sf_path, int(fown), int(fown))
			log("Successfully downloaded " + fpath)

	log("Closing connection to {}:{}...".format(*addr))
	conn.close()
