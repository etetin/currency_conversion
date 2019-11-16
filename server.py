import socket

from client import Client


class Server:
    def __init__(self, host='0.0.0.0', port=8000):
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        self.handlers = []

    def run(self):
        self.socket.listen()
        while True:
            client_socket, client_addr = self.socket.accept()
            self.handle_client(client_socket=client_socket)

            client_socket.close()

    def handle_client(self, client_socket):
        client = Client(client_socket, self.handlers)
        request = client.parse_request()
        response = client.handle_request(request=request)
        if response is None:
            # TODO return 404 or 405
            response = 404, '''
                <html>
                    <head>
                        <title>page not found</title>
                    </head>
                    <body>
                        <h1>404 not found</h1>
                    </body>
                </html>'''

        client.send_response(response=response)

    def get(self, path):
        def decorator(f):
            class Handler:
                def can_handle(self, request):
                    return request.method == 'GET' and request.path == path

                def handle(self, request):
                    return f(request)

            self.handlers.append(Handler())
            return f

        return decorator


server = Server()


@server.get('/')
def root(request):
    return 200, '''
        <html>
            <head>
                <title>index page</title>
            </head>
            <body>
                <h1>hello</h1>
            </body>
        </html>'''


server.run()
