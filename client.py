from copy import copy


class Request:
    pass


class Client:
    def __init__(self, socket, handlers):
        self.socket = socket
        self.handlers = handlers

    def handle_request(self, request):
        for handler in self.handlers:
            if handler.can_handle(request=request):
                return handler.handle(request)
        else:
            return None  # no handlers

    def parse_request(self):
        raw_request = self.socket.recv(4096).decode('utf-8').splitlines()

        request = Request()
        request_info = raw_request.pop(0)
        request.method, request.path, request.http_version = request_info.split()  # METHOD /path HTTP/version
        request.data = raw_request.pop()

        # TODO parse headers
        request.headers = copy(raw_request)

        return request

    def send_response(self, response):
        code, body = response
        body = body.encode()

        code_name = {
            200: 'OK',
            404: 'Not Found',
        }[code]

        self.socket.send(f'HTTP/1.0 {code} {code_name}\r\n'.encode())

        self.socket.send(body)

