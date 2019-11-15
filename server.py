import socket

from client import Client


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

            self.handle_client(client_socket=client_socket)
            client_socket.close()

    @staticmethod
    def handle_client(client_socket):
        client = Client(client_socket)
        client.handle()


server = Server()
server.run()
