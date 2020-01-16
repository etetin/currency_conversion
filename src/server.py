import sys
import traceback
import socket
import json
import http.client
from datetime import datetime
from typing import Callable, Tuple, Union

from .client import Client, Request


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
