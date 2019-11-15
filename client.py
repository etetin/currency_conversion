class Client:
    def __init__(self, socket):
        self.socket = socket

    def handle(self):
        request = self.socket.recv(4096)
        if request:
            self.socket.send(b'hello\n')
        else:
            self.socket.close()
