
import logging
import socket
import ssl
import time


logger = logging.getLogger("legato.util.ssl_socket")


class ResilientSSLSocket(object):
    DEFAULT_MAX_RETRY_COUNT = 5
    DEFAULT_RETRY_INTERVAL  = 1

    def __init__(self, host, port,
                 private_key_file=None, cert_file=None, ca_certs_file=None,
                 max_retry_count=3, retry_interval=5):
        super().__init__()
        self.host = host
        self.port = port
        self.private_key_file = private_key_file
        self.cert_file = cert_file
        self.ca_certs_file = ca_certs_file
        self.max_retry_count = max_retry_count
        self.retry_interval = retry_interval
        self.sock = self._init_ssl_socket()

    def _init_ssl_socket(self):
        logger.debug("Initializing SSL socket: host='%s', port=%d ...", self.host, self.port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cert_reqs = ssl.CERT_REQUIRED if self.ca_certs_file is not None else ssl.CERT_NONE
        ssl_sock = ssl.wrap_socket(sock, keyfile=self.private_key_file, certfile=self.cert_file, cert_reqs=cert_reqs,
                                   ssl_version=ssl.PROTOCOL_SSLv23, ca_certs=self.ca_certs_file)
        ssl_sock.connect((self.host, self.port))
        logger.debug("SSL socket initialized: host='%s', port=%d", self.host, self.port)
        return ssl_sock

    def close(self):
        self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.close()
        except:
            logger.exception("Unexpected exception while closing SSL socket")

    def _reconnect(self):
        logger.warning("Reconnecting to SSL socket: host='%s', port=%d ...", self.host, self.port)

        try:
            self.close()
        except socket.error:
            logger.exception("An error was encountered while closing SSL socket: host='%s', port=%d. Ignored",
                             self.host, self.port)

        self.sock = self._init_ssl_socket()

    def write(self, data):
        retry_count = 0
        while True:
            try:
                return self.sock.write(data)
            except BrokenPipeError as e:
                logger.exception(
                    "An error was encountered while writing data to SSL socket: host='%s', port=%d",
                    self.host, self.port)
                if retry_count < self.max_retry_count:
                    retry_count += 1
                    time.sleep(self.retry_interval)
                    self._reconnect()
                else:
                    raise e
