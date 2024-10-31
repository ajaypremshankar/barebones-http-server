import os

from app.models import ServerOptions
from app.single_request import SingleRequest


class RequestHandler:
    @staticmethod
    def handle(server_options: ServerOptions,
               single_request: SingleRequest):
        req_method, req_path, req_headers, req_body = single_request.request
        base_path = req_path.split("/")
        match [req_method, base_path[1]]:
            case ["GET", ""]:
                single_request.status("200 OK").send_all()
            case ["GET", "echo"]:
                body = base_path[2]
                single_request.status("200 OK").body(body).send_all()
            case ["GET", "user-agent"]:
                user_agent = req_headers.get("User-Agent")
                single_request.status("200 OK").body(user_agent).send_all()
            case ["GET", "files"]:
                full_path = os.path.join(str(server_options.server_path), str(base_path[2]))

                try:
                    f = open(full_path, "r")
                    content = f.read()
                    single_request.status("200 OK").headers({
                        "Content-Type": "application/octet-stream"}).body(content).send_all()
                except FileNotFoundError:
                    single_request.status("404 Not Found").send_all()
            case ["POST", "files"]:
                full_path = os.path.join(str(server_options.server_path), str(base_path[2]))

                with open(full_path, "w") as f:
                    f.write(req_body)
                    f.close()

                single_request.status("201 Created").send_all()
