import socket
from typing import Tuple


class Request:
    method = None
    path = None
    data = None


class Client:
    def __init__(self, client_socket: socket.socket, handlers: list) -> None:
        self.socket = client_socket
        self.handlers = handlers

    def handle_request(self, request: Request) -> Tuple[int, str]:
        for handler in self.handlers:
            if handler.can_handle(request=request):
                return handler.handle(request)
        # `else` case is unreachable because we have handler `any`

    def parse_request(self) -> Request:
        raw_request = self.socket.recv(4096).decode('utf-8').splitlines()

        request = Request()
        request_info = raw_request.pop(0)
        request.method, request.path, request.http_version = request_info.split()  # METHOD /path HTTP/version

        end_of_headers = raw_request.index('')
        # TODO parse headers
        request.headers = raw_request[:end_of_headers]
        request.data = '\n'.join(raw_request[end_of_headers+1:])
        del raw_request

        return request

    def send_response(self, response: Tuple[int, str]) -> None:
        code, body = response
        body = body.encode()

        code_name = {
            200: 'OK',
            400: 'Bad Request',
            404: 'Not Found',
            405: 'Method Not Allowed',
            415: 'Unsupported Media Type',
        }[code]

        self.socket.send(f'HTTP/1.0 {code} {code_name}\r\n'.encode())

        self.send_header('Content-type', 'application/json')
        self.socket.send(b'\r\n')  # finish headers

        self.socket.send(body)

    def send_header(self, name: str, value: str) -> None:
        self.socket.send(f'{name}: {value}\r\n'.encode())

