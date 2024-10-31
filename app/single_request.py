import socket

from app.handlers.compression_handler import CompressionHandler
from app.models import RequestPayload, ResponsePayload


class SingleRequest:
    def __init__(self, sock: socket.socket):
        self._socket = sock
        self._response = None
        self._request = None

    def handle_request(self):
        req_buff = self._socket.recv(1024)
        self._parse_request_buffer(req_buff.decode())

    def respond(self, status: str, headers = None, body = None):
        self._response = ResponsePayload(status, headers or {}, body or "")
        self._send_all()

    def get_request_header(self, key, default = None):
        return self._request.headers.get(key, default)

    def get_response_header(self, key, default = None):
        return self._response.headers.get(key, default)

    def set_response_header(self, key, val):
        self._response.headers[key] = val

    def set_request_header(self, key, val):
        self._request.headers[key] = val

    def get_request(self):
        return self._request

    def _parse_request_buffer(self, buff: str):
        split_buff = buff.split("\r\n\r\n", maxsplit=1)
        split_req_line_and_header = split_buff[0].split("\r\n")

        request_line = split_req_line_and_header[0].split(" ")

        headers = {}

        for h in split_req_line_and_header[1:]:
            h_kv = h.split(":", maxsplit=1)
            headers[h_kv[0]] = h_kv[1].strip()

        self._request = RequestPayload(
            method=request_line[0],
            path=request_line[1],
            headers=headers,
            body=split_buff[1]
        )

    def _create_response(self):

        compression_handler = CompressionHandler.get(self.get_request_header("Accept-Encoding", ""))
        is_compression_applicable = compression_handler is not None

        response_payload = self._response

        response_body = response_payload.body

        if is_compression_applicable:
            response_body = compression_handler.compress(response_body)
            self.set_response_header('Content-Encoding', compression_handler.name())

        # add common headers
        self.set_response_header("Content-length", len(response_body))

        if not response_payload.headers.get("Content-Type"):
            self.set_response_header("Content-Type", "text/plain")

        headers_str = ""
        for k, v in (self._response.headers or {}).items():
            headers_str += f"{k.strip()}: {str(v).strip()}\r\n"

        if is_compression_applicable:
            return f"HTTP/1.1 {response_payload.status}\r\n{headers_str}\r\n".encode() + response_body
        else:
            return f"HTTP/1.1 {response_payload.status}\r\n{headers_str}\r\n{response_body}".encode()

    def _send_all(self):
        self._socket.sendall(self._create_response())
        self._socket.close()