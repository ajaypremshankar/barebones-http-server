import threading
import socket

from lark.tools import options

from app.handlers.request_handler import RequestHandler
from app.models import ServerOptions
from app.single_request import SingleRequest

class BarebonesServer:
    def __init__(self, server_path: str, address: tuple[str, int]):
        self.options = ServerOptions(server_path)
        self.server_socket = socket.create_server(address, reuse_port=True)

    def start_server(self):
        while True:
            sock, response_addr = self.server_socket.accept()
            t = threading.Thread(target=lambda: self.spawn_requests(sock))
            t.start()

    def spawn_requests(self, sock: socket.socket):
        single_request = SingleRequest(sock)
        single_request.handle_request()

        RequestHandler.handle(server_options=self.options, single_request=single_request)
