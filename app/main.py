import os.path
import socket
import sys
import threading
import zlib

base_path = None


def create_http_response(status, headers=None, body=""):
    headers_str = ""
    if headers is not None:
        for k, v in headers.items():
            headers_str += f"{k.strip()}:{str(v).strip()}\r\n"

    return f"HTTP/1.1 {status}\r\n{headers_str}\r\n{body}"

def create_http_response_compressed(status, headers, body):
    headers_str = ""
    if headers is not None:
        for k, v in headers.items():
            headers_str += f"{k.strip()}:{str(v).strip()}\r\n"

    return f"HTTP/1.1 {status}\r\n{headers_str}\r\n".encode() + body


def parse_buffer(buff):
    split_buff = buff.split("\r\n\r\n", maxsplit=1)
    split_header = split_buff[0].split("\r\n")

    request_line = split_header[0].split(" ")

    headers = {}

    for h in split_header[1:]:
        h_kv = h.split(":", maxsplit=1)
        headers[h_kv[0]] = h_kv[1].strip()

    return {
        "method": request_line[0],
        "path": request_line[1],
        "headers": headers,
        "body": split_buff[1]
    }


def send_all(sock: socket.socket, status, headers=None, body="", compressed = False):
    if compressed:
        sock.sendall(create_http_response_compressed(status, headers, body))
    else:
        sock.sendall(create_http_response(status, headers, body).encode())
    sock.close()


def get_supported_request_encoding(headers: dict):
    accept_encodings = headers.get("Accept-Encoding", "").split(",")
    accept_encodings = [x.strip() for x in accept_encodings]

    return 'gzip' if 'gzip' in accept_encodings else None


def handle_request(sock: socket.socket):
    buff = sock.recv(1024)

    parsed_request = parse_buffer(buff.decode())

    path = parsed_request.get("path", "/")
    method = parsed_request.get("method")

    if path == "/":
        sock.sendall(create_http_response("200 OK").encode())

    elif method == 'GET' and path.startswith("/echo/"):
        path_split = path.rsplit("/", 1)
        echo_val = path_split[1]

        resp_headers = {
            "Content-Type": "text/plain"
        }

        content = echo_val

        request_encoding = get_supported_request_encoding(parsed_request.get("headers", {}))

        compressed = request_encoding == 'gzip'
        if compressed:
            content = zlib.compress(echo_val.encode())
            resp_headers['Content-Encoding'] = 'gzip'

        resp_headers["Content-length"] = len(content)

        send_all(sock, "200 OK", resp_headers, content, compressed)
    elif method == 'GET' and path == '/user-agent':
        user_agent = parsed_request.get("headers").get("User-Agent")

        send_all(sock, "200 OK", {
            "Content-Type": "text/plain",
            "Content-length": len(user_agent)
        }, user_agent)

    elif method == 'GET' and path.startswith('/files'):

        if base_path is None:
            send_all(sock, "404 Not Found")

        path_split = path.rsplit("/", 1)
        file_path = path_split[1]

        full_path = os.path.join(str(base_path), str(file_path))

        try:
            f = open(full_path, "r")
            content = f.read()
            send_all(sock, "200 OK", {
                "Content-Type": "application/octet-stream",
                "Content-length": len(content)
            }, content)
        except FileNotFoundError:
            send_all(sock, "404 Not Found")
    elif method == 'POST' and path.startswith("/files"):
        path_split = path.rsplit("/", 1)
        file_path = path_split[1]
        full_path = os.path.join(str(base_path), str(file_path))

        body = parsed_request.get("body", "")

        f = open(full_path, "w")
        f.write(body)

        send_all(sock, "201 Created")

    else:
        send_all(sock, "404 Not Found")


def main():
    global base_path

    if len(sys.argv) >= 2:
        base_path = sys.argv[2]

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        sock, response_addr = server_socket.accept()
        t = threading.Thread(target=lambda: handle_request(sock))
        t.start()


if __name__ == "__main__":
    main()
