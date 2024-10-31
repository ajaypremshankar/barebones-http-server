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

        compression_handler = CompressionHandler.get(self._request.headers.get("Accept-Encoding", ""))
        is_compression_applicable = compression_handler is not None

        response_payload = self._response

        body = response_payload.body
        if is_compression_applicable:
            body = compression_handler.compress(body)
            response_payload.headers['Content-Encoding'] = compression_handler.name()

        # add common headers
        response_payload.headers["Content-length"] = len(body)

        if not response_payload.headers.get("Content-Type"):
            response_payload.headers["Content-Type"] = "text/plain"

        headers_str = ""
        if response_payload.headers is not None:
            for k, v in response_payload.headers.items():
                headers_str += f"{k.strip()}: {str(v).strip()}\r\n"

        if is_compression_applicable:
            return f"HTTP/1.1 {response_payload.status}\r\n{headers_str}\r\n".encode() + body
        else:
            return f"HTTP/1.1 {response_payload.status}\r\n{headers_str}\r\n{body}".encode()

    def _send_all(self):
        self._socket.sendall(self._create_response())
        self._socket.close()