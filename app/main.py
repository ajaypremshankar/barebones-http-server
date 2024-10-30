import socket  # noqa: F401
import threading
from threading import Thread


def create_http_response(status, headers="", body=""):
    return f"HTTP/1.1 {status}\r\n{headers}\r\n\r\n{body}"


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
        resp_headers = f"Content-Type: text/plain\r\nContent-Length: {len(echo_val)}"

        sock.sendall(create_http_response("200 OK", resp_headers, echo_val).encode())
        sock.close()
    elif method == 'GET' and path == '/user-agent':
        user_agent = parsed_request.get("headers").get("User-Agent")
        resp_headers = f"Content-Type: text/plain\r\nContent-Length: {len(user_agent)}"
        sock.sendall(create_http_response("200 OK", resp_headers, user_agent).encode())
        sock.close()
    else:
        sock.sendall(create_http_response("404 Not Found").encode())

def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        sock, response_addr = server_socket.accept()
        t = threading.Thread(target=lambda: handle_request(sock))
        t.start()

if __name__ == "__main__":
    main()
