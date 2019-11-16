import os
import sys
import socket
import json
import urllib3

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
        client.send_response(response=response)

    def post(self, path):
        def decorator(f):
            class Handler:
                def can_handle(self, request):
                    return request.method == 'POST' and request.path == path

                def handle(self, request):
                    return f(request)

            self.handlers.append(Handler())
            return f

        return decorator

    def status_404(self):
        def decorator(f):
            class Handler:
                def can_handle(self, request):
                    return True

                def handle(self, request):
                    return f(request)

            self.handlers.append(Handler())
            return f

        return decorator


try:
    app_id = os.environ['APP_ID']
except KeyError:
    sys.exit('Variable APP_ID is not setted. exit')

server = Server()


@server.post('/convert')
def convert(request):
    try:
        data = json.loads(request.data)
    except json.decoder.JSONDecodeError:
        # TODO return 415
        pass

    # validate data
    if 'amount' not in data or \
            not (
                    isinstance(data['amount'], int) or
                    isinstance(data['amount'], float)
            ) or data['amount'] < 0:
        # TODO return 400
        pass

    http = urllib3.PoolManager()
    response = http.request(
        method='GET',
        url=f'https://openexchangerates.org/api/latest.json?app_id={app_id}&?base=USD'
    )

    rub_rate = json.loads(response.data.decode('utf-8'))['rates']['RUB']

    return 200, json.dumps({'result': round(data['amount'] * rub_rate, 2)})


@server.status_404()
def not_found(request):
    return 404, '''
        <html>
            <head>
                <title>page not found</title>
            </head>
            <body>
                <h1>404 not found</h1>
            </body>
        </html>'''


server.run()
