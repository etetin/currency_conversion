import os
import sys
import argparse
import socket
import json
import http.client

from client import Client


class Server:
    def __init__(self, host='0.0.0.0', port=5000):
        print(f'Server initialized by address - {host}:{port}')
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


parser = argparse.ArgumentParser()
parser.add_argument('--host')
parser.add_argument('--port')
args = parser.parse_args()

custom_server_params = {}
if args.host is not None:
    custom_server_params['host'] = args.host

if args.port is not None:
    custom_server_params['port'] = int(args.port)

server = Server(**custom_server_params)


@server.post('/convert')
def convert(request):
    try:
        data = json.loads(request.data)
    # TODO im not sure that this is correct exception
    except json.decoder.JSONDecodeError:
        return 415, json.dumps({'error': 'Unsupported Media Type'})

    # validate data
    if not isinstance(data, dict) or 'amount' not in data or \
            not (
                    isinstance(data['amount'], int) or
                    isinstance(data['amount'], float)
            ) or data['amount'] < 0:
        return 400, json.dumps({'error': 'Wrong params'})

    connection = http.client.HTTPConnection('openexchangerates.org', 80)
    connection.request("GET", f"/api/latest.json?app_id={app_id}&?base=USD")
    response = connection.getresponse()
    rub_rate = json.loads(response.read().decode('utf-8'))['rates']['RUB']

    # TODO need to add in response additional info like: from, to, timestamp, etc
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

# TODO add README
# TODO create tests
# TODO add type annotation
# TODO add logging

# optional
# TODO daemon for restarting if script failed
