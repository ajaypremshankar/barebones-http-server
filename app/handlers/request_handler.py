import os

from app.models import ServerOptions
from app.single_request import SingleRequest


class RequestHandler:
    @staticmethod
    def handle(server_options: ServerOptions,
               single_request: SingleRequest):

        payload = single_request.get_request()

        req_method = payload.method
        req_path = payload.path
        req_headers = payload.headers
        req_body = payload.body
        base_path = req_path.split("/")
        match [req_method, base_path[1]]:
            case ["GET", ""]:
                single_request.respond("200 OK")
            case ["GET", "echo"]:
                body = base_path[2]
                single_request.respond(status="200 OK", body=body)
            case ["GET", "user-agent"]:
                user_agent = req_headers.get("User-Agent")
                single_request.respond(status="200 OK", body=user_agent)
            case ["GET", "files"]:
                full_path = os.path.join(str(server_options.server_path), str(base_path[2]))

                try:
                    f = open(full_path, "r")
                    content = f.read()
                    single_request.respond(status="200 OK", headers={
                        "Content-Type": "application/octet-stream"}, body=content)
                except FileNotFoundError:
                    single_request.respond(status="404 Not Found")
            case ["POST", "files"]:
                full_path = os.path.join(str(server_options.server_path), str(base_path[2]))

                with open(full_path, "w") as f:
                    f.write(req_body)
                    f.close()

                single_request.respond(status="201 Created")
