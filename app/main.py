import socket  # noqa: F401


def create_http_response(status, headers="", body=""):
    return f"HTTP/1.1 {status}\r\n{headers}\r\n{body}"


def parse_buffer(buff):
    split_buff = buff.split("\r\n\r\n", maxsplit=1)
    split_header = split_buff[0].split("\r\n")

    request_line = split_header[0].split(" ")

    headers = []

    for h in split_header[1:]:
        h_kv = h.split(":")
        headers.append({
            "key": h_kv[0],
            "value": h_kv[1].strip()
        })

    return {
        "method": request_line[0],
        "path": request_line[1],
        "headers,": headers,
        "body": split_buff[1]
    }


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    accept = server_socket.accept()
    connection = accept[0]

    buff = connection.recv(1024)

    parsed_request = parse_buffer(buff.decode())

    if parsed_request.get("path") != "/":
        connection.sendall(create_http_response("404 Not Found").encode())
    else:
        connection.sendall(create_http_response("200 OK").encode())


if __name__ == "__main__":
    main()
