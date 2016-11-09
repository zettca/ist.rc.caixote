import socket
import sys

HOST = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
PORT = sys.argv[2] if len(sys.argv) > 2 else 59999
USER = sys.argv[3] if len(sys.argv) > 3 else "zettca"
DIR = sys.argv[4] if len(sys.argv) > 4 else "home"
ENCODING = "utf-8"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

while True:
	inpute = input("< ")
	s.sendall(bytes(inpute + "\n", ENCODING))
	data = str(s.recv(1024), ENCODING)
	print("> " + data)
s.close()