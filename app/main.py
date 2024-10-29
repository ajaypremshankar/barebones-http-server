import socket  # noqa: F401

def create_http_response(status, headers = "", body = ""):
    return f"HTTP/1.1 {status}\r\n{headers}\r\n{body}"

def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.accept()[0].sendall(create_http_response("200 OK").encode())


if __name__ == "__main__":
    main()
