import socket


class Server:
    def __init__(self, host='0.0.0.0', port=8000):
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))

    def run(self):
        self.socket.listen()
        while True:
            client_socket, client_addr = self.socket.accept()
            print('client here')
            client_socket.close()


server = Server()
server.run()
