import time
import os

ROOT_PATH = "files"
logged_sockets = []

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

def client_thread_handler(sock):
	conn, addr = sock["conn"], sock["addr"]

	uaddr = "{}:{}".format(*addr)
	log("{} bound to thread...".format(uaddr))

	while True:
		# Get Header line, split by spaces
		headers = readline_split_utf8(conn)
		if not headers: # client exited early
			log("{} closed socket? :(".format(uaddr))
			global logged_sockets # V "logout" if logged in
			logged_sockets = [s for s in logged_sockets if s["addr"] != addr]
			break

		# Get/Split header line
		print(headers)
		method, header = headers[0], headers[1:]

		if method == "LOG":
			sock["uname"], sock["upath"] = header
			uname, upath = sock["uname"], sock["upath"]
			filt = lambda s : s["uname"] == uname and s["upath"] == upath
			if not contains(logged_sockets, filt):
				logged_sockets.append(sock)
				log("{} logged in as {} to sync {}...".format(uaddr, uname, upath))
				conn.sendall(b"LOGGED PlsSendINF...\n")
			else:
				log("{} tried to double sync {}:{}. Already being synced...".format(uaddr, uname, upath))
				conn.sendall(b"ERRORE Alreadysyncingpath...\n")
				break

		elif method == "INF":
			num_lines = header
			urpath = os.path.join(ROOT_PATH, sock["uname"])
			os.makedirs(urpath, exist_ok=True)

			for _ in range(int(num_lines)):
				line = readline_split_utf8(conn)
				fmtime, fown, fpath = int(line[0]), int(line[1]), os.path.join(urpath, line[2])
				print(fpath)
				if not os.path.exists(fpath): # file doesn't exist
					print("File at {} named {} doesn't exist!".format(*os.path.split(fpath)))
					os.makedirs(os.path.dirname(fpath), exist_ok=True) # make dirs if doesn't exist
					print("File " + fpath + " does not exist. Creating...")
					with open(fpath, "a"):
						os.utime(fpath, (0, 0))
						os.chown(fpath, fown, fown)
					print("Client must send " + fpath)
				elif os.path.isfile(fpath):
					stats = os.lstat(fpath)
					if int(stats.st_mtime) > fmtime:
						print(fpath + " should be sent to client")
					elif int(stats.st_mtime) < fmtime:
						print(fpath + " outdated. pls send client!")
					else:
						print(fpath + " is up to date!")
				else:
					print("Directory or weird file? Do nothing!")

		elif method == "GET":
			print("not yet implemented.")
			conn.sendall("not yet implemented. sorry client.")

		elif method == "PUT":
			print("not yet implemented.")
			conn.sendall("not yet implemented. sorry client.")

		else:
			print("Method not valid. Not treated yet tho")
			print("... ?")

		#conn.sendall(b"(End of HEADER check)")

	log("Closing connection to {}:{}...".format(*addr))
	conn.close()
