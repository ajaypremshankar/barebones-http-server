import threading
import socket

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
            t = threading.Thread(target=lambda: self.handle_request(sock))
            t.start()

    def handle_request(self, sock: socket.socket):
        single_request = SingleRequest(sock)
        single_request.receive_request()

        RequestHandler.handle(self.options, single_request=single_request)
