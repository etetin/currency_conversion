import os
import sys
import traceback
import argparse
import socket
import json
import http.client
from datetime import datetime
from typing import Callable, Tuple, Union

from client import Client, Request


def get_rate() -> Tuple[Union[int, float], str]:
    connection = http.client.HTTPConnection('openexchangerates.org', 80)
    connection.request("GET", f"/api/latest.json?app_id={app_id}&?base=USD")
    response = json.loads(connection.getresponse().read().decode('utf-8'))
    rub_rate = response['rates']['RUB']
    # notice that this datetime will be in server timezone
    # i'm not sure can i use `pytz`, so i don't wanna romp with default library
    state_at = datetime.fromtimestamp(response['timestamp']).strftime('%Y-%m-%d %H:%M:%S')

    return rub_rate, state_at


class Server:
    def __init__(self, host: str = '0.0.0.0', port: int = 5000) -> None:
        print(f'Server initialized by address - {host}:{port}')
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        self.handlers = []

    def run(self) -> None:
        self.socket.listen()
        while True:
            client_socket, client_addr = self.socket.accept()
            self.handle_client(client_socket=client_socket)

            client_socket.close()

    def handle_client(self, client_socket: socket.socket) -> None:
        client = Client(client_socket, self.handlers)
        request = client.parse_request()
        try:
            response = client.handle_request(request=request)
        except:
            _, ex, tb = sys.exc_info()
            tb_message = '\r'.join(traceback.format_tb(tb))
            err_message = str(ex)
            response = (500, 'smth gone wrong')
            f = open("error.log", "a")
            f.write(f'{datetime.now()}\n{tb_message}{err_message}\r\n\r\n')
            f.close()
        finally:
            client.send_response(response=response, request=request)

    def post(self, path: str) -> Callable[[Request], Callable[[Request], Tuple[int, str]]]:
        def decorator(f) -> Callable[[Request], Tuple[int, str]]:
            class Handler:
                def can_handle(self, request: Request) -> bool:
                    # TODO what if url path is exist, but method is not allowed?
                    return request.method == 'POST' and request.path == path

                def handle(self, request: Request) -> Tuple[int, str]:
                    return f(request)

            self.handlers.append(Handler())
            return f

        return decorator

    def status_404(self) -> Callable[[Request], Callable[[Request], Tuple[int, str]]]:
        def decorator(f):
            class Handler:
                def can_handle(self, request: Request) -> bool:
                    return True

                def handle(self, request: Request) -> Tuple[int, str]:
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
# TODO may be validation for passed arguments?
if args.host is not None:
    custom_server_params['host'] = args.host

if args.port is not None:
    custom_server_params['port'] = int(args.port)

server = Server(**custom_server_params)


@server.post('/convert')
def convert(request: Request) -> Tuple[int, str]:
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

    # not best decision to make request every time, because data updated hourly
    # for example, we can store this data on server side and update them also hourly
    rub_rate, state_at = get_rate()

    respnose_data = {
        'result': round(data['amount'] * rub_rate, 2),
        'from': 'USD',
        'to': 'RUB',
        'state_at': state_at
    }
    return 200, json.dumps(respnose_data)


@server.status_404()
def not_found(request: Request) -> Tuple[int, str]:
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

# TODO create tests

# optional
# TODO daemon for restarting if script failed
