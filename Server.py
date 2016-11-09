import socketserver
import sys

HOST = 'localhost'
PORT = sys.argv[1] if len(sys.argv) > 1  else 59999

class TCPHandler(socketserver.BaseRequestHandler):
	def handle(self):
		# self.request is the TCP socket connected to the client
		self.data = self.request.recv(1024).strip()
		print("{} wrote:".format(self.client_address[0]))
		print(self.data)
		# just send back the same data, but upper-cased
		self.request.sendall(self.data.upper())

# ServerSocket creation/activation
server = socketserver.TCPServer((HOST, PORT), TCPHandler)
server.serve_forever()
