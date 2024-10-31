from dataclasses import dataclass


@dataclass
class ServerOptions:
    server_path: str


@dataclass
class RequestPayload:
    method: str
    path: str
    headers: dict
    body: str

@dataclass
class ResponsePayload:
    status: str
    headers: dict
    body: str

