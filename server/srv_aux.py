import time
import os

ENCODING = "utf8"
ROOT_PATH = "files"
SLEEP_TIME = 2 # seconds
logged_sockets = []

def log(msg):
	print("[{}] {}".format(time.strftime("%H:%M:%S", time.localtime()), msg))

def recv_bytes(conn, len):
	res = b""
	try:
		res = conn.recv(len)
	except Exception as e:
		log("The following error ocurred while reading from socket:")
		log(e)
		return None
	return res

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
		byte = recv_bytes(conn, 1)
		if not byte or byte == b"\n": break
		byteses += byte
	try:
		return str(byteses, ENCODING).split(" ")
	except Exception as e:
		log(e)
		return []

def make_line_bytes(lst):
	lst = [str(el) for el in lst]
	lst[-1] += "\n"
	return bytes(" ".join(lst), ENCODING)

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
	fbytes = recv_bytes(conn, flength)
	while len(fbytes) < flength: # sometimes recv doesn't receive all bytes
		fbytes += recv_bytes(conn, flength - len(fbytes))
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
	conn.sendall(make_line_bytes(["FILE", cf_path, len(fbytes), int(stats.st_mtime)]))
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
			break

		#log(data)
		method, headers = data[0], data[1:] # Split header line

		if method == "LOGIN": # CLIENT REQUESTED "LOGIN" 
			uname, upath = headers[0], headers[1]
			sock["uname"], sock["upath"] = uname, upath
			if login_user(sock, uname, upath):
				log("Client {}:{} identified as {}".format(addr[0], addr[1], uname))
				conn.sendall(make_line_bytes(["LOGGED", "IN"]))
			else:
				conn.sendall(make_line_bytes(["LOGGED", "OUT"]))
				break

		elif "uname" not in sock and "upath" not in sock:
			log("Unauthenticated client issued non-login method")
			break

		elif method == "DIFF": # CLIENT REQUESTED FILES INFOS
			log("Client {} requested files DIFF".format(sock["uname"]))
			response = make_file_diffs(sock, headers)
			conn.sendall(make_line_bytes(["DIFFS", len(response)]))
			for line in response:
				log("Requesting file " + line[1])
				conn.sendall(make_line_bytes(line))

		elif method == "GET": # CLIENT REQUESTED FILE CONTENTS
			cf_path = headers[0]
			log("Uploading {}...".format(cf_path))
			time.sleep(SLEEP_TIME)
			send_file(sock, cf_path)
			log("Uploaded " + cf_path)

		elif method == "GETN": # CLIENT REQUESTED N FILES' CONTENTS
			num_lines = headers[0]
			for _ in range(int(num_lines)):
				cf_path = readline_split(conn)[0]
				log("Uploading {}...".format(cf_path))
				time.sleep(SLEEP_TIME)
				send_file(sock, cf_path)
				log("Uploaded " + cf_path)

		elif method == "PUT": # CLIENT SENT FILES CONTENTS
			cf_path, flength, fmtime = headers[0], headers[1], headers[2]
			log("Downloading {}...".format(cf_path))
			time.sleep(SLEEP_TIME)
			save_file(sock, cf_path, int(flength), fmtime)
			log("Downloaded " + cf_path)

		elif method == "EXIT":
			log("Client {} safely closed connection".format(sock["uname"]))

		elif method:
			log("Unknown method: {}. Ignoring".format(method))

		else:
			log("Killing connection to {}:{}".format(*addr))
			break

	remove_from_socketlist(sock)
	conn.close()
	log("Closed connection to {}:{}".format(*addr))
