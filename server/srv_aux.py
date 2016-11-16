import time
import os

ENC = "utf8"
ROOT_PATH = "files"
logged_sockets = []

def log(msg):
	print("[{}] {}".format(time.strftime("%H:%M:%S", time.localtime()), msg))

def login_user(sock, uname, upath):
	for s in logged_sockets:
		if s["uname"] == uname and s["upath"] == upath:
			return False
	logged_sockets.append(sock)
	return True

def remove_from_socketlist(sock):
	for s in logged_sockets:
		if s == sock:
			logged_sockets.remove(s)

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

# ============================================================ #

def get_files_cli_relative(path):
	lst = []
	for path, dirs, files in os.walk(path):
		cli_path = "/".join(path.split("/")[2:]) # removes uname/upath/
		for fi in files:
			lst.append(os.path.join(cli_path, fi))
	return lst

def make_file_diffs(sock, headers):
	num_lines = headers[0]
	urpath = os.path.join(ROOT_PATH, sock["uname"], sock["upath"])
	os.makedirs(urpath, exist_ok=True)

	cli_files, srv_files = [], get_files_cli_relative(urpath)
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

def save_file(sock, cf_path, flength, fmtime):
	conn = sock["conn"]
	fbytes = conn.recv(flength)
	while len(fbytes) < flength: # sometimes recv doesn't receive all bytes
		fbytes += conn.recv(flength - len(fbytes))
		log("Downloading {} [{}/{} {}%]".format(cf_path, len(fbytes), flength, int(100*len(fbytes)/flength)))

	sf_path = os.path.join(ROOT_PATH, sock["uname"], cf_path)
	os.makedirs(os.path.split(sf_path)[0], exist_ok=True)
	with open(sf_path, "wb") as fd:
		fd.write(fbytes)
	os.utime(sf_path, (int(fmtime), int(fmtime)))

def send_file(sock, cf_path):
	conn = sock["conn"]
	sf_path = os.path.join(ROOT_PATH, sock["uname"], cf_path)
	stats = os.lstat(sf_path)
	with open(sf_path, "rb") as fd:
		fbytes = fd.read()
	conn.sendall(make_line_bytes(["TOSAVE", cf_path, len(fbytes), int(stats.st_mtime)]))
	conn.sendall(fbytes)

# ============================================================ #

def client_handler(sock):
	conn, addr = sock["conn"], sock["addr"]
	log("Client {}:{} bound to thread".format(*addr))

	while True:
		data = readline_split(conn) # Get Header line, split by spaces
		global logged_sockets # V "logout" if logged in
		if not data:
			log("{}:{} sent None. Exiting".format(*addr))
			remove_from_socketlist(sock)
			break

		#log(data)
		method, headers = data[0], data[1:] # Split header line

		if method == "LOG": # CLIENT REQUESTED "LOGIN" 
			uname, upath = headers
			sock["uname"], sock["upath"] = uname, upath
			if login_user(sock, uname, upath):
				log("Client {}:{} identified as {}".format(addr[0], addr[1], uname))
				conn.sendall(b"LOGGED arg2\n")
			else:
				conn.sendall(b"GOAWAY arg2\n")
				break

		elif method == "INF": # CLIENT REQUESTED FILES INFOS
			response = make_file_diffs(sock, headers)
			conn.sendall(make_line_bytes(["TOSYNC", len(response)]))
			for line in response:
				log("Requesting file " + line[1])
				conn.sendall(make_line_bytes(line))

		elif method == "GET": # CLIENT REQUESTED FILE CONTENTS
			fpath = headers[0]
			log("Uploading {}".format(fpath))
			time.sleep(0.6)
			send_file(sock, fpath)
			log("Uploaded " + fpath)

		elif method == "PUT": # CLIENT SENT FILES CONTENTS
			fpath, flength, fmtime = headers
			log("Downloading {}".format(fpath))
			time.sleep(0.6)
			save_file(sock, fpath, int(flength), fmtime)
			log("Downloaded " + fpath)

		elif method:
			log("Unknown method: {}. Ignoring".format(method))

		else:
			log("Files are synced? Killing {}'s' connection...".format(sock["uname"]))
			remove_from_socketlist(sock)
			break

	log("Closing connection to {}:{}".format(*addr))
	conn.close()
