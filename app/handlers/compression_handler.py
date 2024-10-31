import gzip
from abc import abstractmethod


class CompressionHandler:
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def compress(self, payload):
        pass

    @staticmethod
    def get(encoding_header_val):
        accept_encodings = encoding_header_val.split(",")
        accept_encodings = [x.strip() for x in accept_encodings]

        for ae in accept_encodings:
            match ae:
                case 'gzip':
                    return GZipCompressionHandler()
                case _:
                    return None


class GZipCompressionHandler(CompressionHandler):

    def name(self):
        return 'gzip'

    def compress(self, payload: str):
        return gzip.compress(payload.encode())
