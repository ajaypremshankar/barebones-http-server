import gzip
import socket
from dataclasses import dataclass
from typing import Self

from app.models import RequestPayload


class SingleRequest:
    def __init__(self, sock: socket.socket):
        self.socket = sock
        self.status = None
        self.headers = None
        self.body = None
        self.request = None

    def receive_request(self):
        req_buff = self.socket.recv(1024)
        self.parse_request_buffer(req_buff.decode())

    def status(self, status: str) -> Self:
        self.status = status
        return self

    def headers(self, headers: dict) -> Self:
        self.headers = headers
        return self

    def body(self, body: str) -> Self:
        self.body = body
        return self

    def parse_request_buffer(self, buff: str):
        split_buff = buff.split("\r\n\r\n", maxsplit=1)
        split_req_line_and_header = split_buff[0].split("\r\n")

        request_line = split_req_line_and_header[0].split(" ")

        headers = {}

        for h in split_req_line_and_header[1:]:
            h_kv = h.split(":", maxsplit=1)
            headers[h_kv[0]] = h_kv[1].strip()

        self.request = RequestPayload(
            method=request_line[0],
            path=request_line[1],
            headers=headers,
            body=split_buff[1]
        )

    @staticmethod
    def create_http_response(status, headers=None, body=None):

        if not headers:
            headers = {}

        should_compress_body = 'gzip' == SingleRequest.get_supported_request_encoding(headers)

        if should_compress_body:
            body = gzip.compress(body.encode())
            headers['Content-Encoding'] = 'gzip'

        # add common headers
        headers["Content-length"] = len(body)

        if not headers.get("Content-Type"):
            headers["Content-Type"] = "text/plain"

        headers_str = ""
        if headers is not None:
            for k, v in headers.items():
                headers_str += f"{k.strip()}:{str(v).strip()}\r\n"

        if should_compress_body:
            return f"HTTP/1.1 {status}\r\n{headers_str}".encode() + body
        else:
            return f"HTTP/1.1 {status}\r\n{headers_str}\r\n{body}".encode()

    def send_all(self):
        self.socket.sendall(SingleRequest.create_http_response(self.status, self.headers, self.body))
        self.socket.close()

    @staticmethod
    def get_supported_request_encoding(headers: dict):
        accept_encodings = headers.get("Accept-Encoding", "").split(",")
        accept_encodings = [x.strip() for x in accept_encodings]

        return 'gzip' if 'gzip' in accept_encodings else None
