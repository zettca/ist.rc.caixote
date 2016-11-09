import socketserver
import sys

HOST = 'localhost'
PORT = sys.argv[1] if len(sys.argv) > 1  else 59999

class TCPHandler(socketserver.BaseRequestHandler):
	def handle(self):
		print(self.request) # TCP socket connected to the client
		self.data = self.request.recv(1024).strip()
		print("{}:{} wrote: {}".format(*self.client_address, self.data))
		self.request.sendall(self.data.upper()) # send recv upcased

# ServerSocket creation/activation
server = socketserver.TCPServer((HOST, PORT), TCPHandler)
server.serve_forever()
