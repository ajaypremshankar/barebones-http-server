import socket  # noqa: F401


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


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    accept = server_socket.accept()
    connection = accept[0]

    buff = connection.recv(1024)

    parsed_request = parse_buffer(buff.decode())

    path = parsed_request.get("path", "/")
    method = parsed_request.get("method")
    if path == "/":
        connection.sendall(create_http_response("200 OK").encode())

    elif method == 'GET' and path.startswith("/echo/"):
        path_split = path.rsplit("/", 1)
        echo_val = path_split[1]
        resp_headers = f"Content-Type: text/plain\r\nContent-Length: {len(echo_val)}"

        connection.sendall(create_http_response("200 OK", resp_headers, echo_val).encode())
        connection.close()
    elif method == 'GET' and path == '/user-agent':
        user_agent = parsed_request.get("headers").get("User-Agent")
        resp_headers = f"Content-Type: text/plain\r\nContent-Length: {len(user_agent)}"
        connection.sendall(create_http_response("200 OK", resp_headers, user_agent).encode())
        connection.close()
    else:
        connection.sendall(create_http_response("404 Not Found").encode())



if __name__ == "__main__":
    main()
