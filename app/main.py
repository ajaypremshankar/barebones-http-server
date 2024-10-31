import os.path
import sys

from app.server import BarebonesServer


def main():

    base_path = os.getcwd()
    if len(sys.argv) >= 2:
        base_path = sys.argv[2]

    barebones_server = BarebonesServer(base_path, ("localhost", 4221))
    barebones_server.start_server()


if __name__ == "__main__":
    main()
