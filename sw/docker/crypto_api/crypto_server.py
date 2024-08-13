import threading
from threading import current_thread
import socket
import logging

ENCODE_PORT = 2005
DECODE_PORT = 2006

def setup_logger(log_file):
    logger = logging.getLogger('encryption_server_logger')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - [%(filename)s:%(lineno)d] - %(message)s')

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

logger = setup_logger('./log.txt')

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

def encode_data(data):
    return data

def encoder(conn, client_id, address):
    try:
        logger.info(f'Client#{client_id} get client at {address}')
    except Exception as e:
        logger.info(f'Exception:{e}\nclient#{client_id} connection closed')
        if conn:
            conn.close()
        return
            
    while conn:
        try: 
            data = conn.recv(2048)
            if not data:
                logger.info(f"Current socket closed by client#{client_id} from {address}")
                conn.close()
                conn = None
                break
            logger.info(f"Received from client#{client_id}:{data}")
            encoded = encode_data(data)
            conn.send(encoded)
        except Exception as e:
            logger.info(f'client#{client_id}: Exception: {e}')
            continue

    if conn:
        conn.close()  # close the connection
        conn = None

def server(port, handler):
    client_id = 1 if port == ENCODE_PORT else 100001
    while True:
        try:
            server_socket = socket.socket()
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('0.0.0.0', port))
            server_socket.listen(100000)

            while True:
                logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                logger.info(f"Waiting for client connection at {port}")
                conn, address = server_socket.accept()  # accept new connection
                logger.info(f"Client #{client_id} connected from: {address}. Create a thread...")
                _handler_thread = StoppableThread(target=handler, args=(conn, client_id, address,))
                _handler_thread.start()
                client_id += 1

        except Exception as e:
            server_socket.close()
            server_socket = None
            logger.info(e)

def main():
    try:
        _encoder_thread = StoppableThread(target=server,args=(ENCODE_PORT, encoder,))
        _encoder_thread.start()
        _decoder_thread = StoppableThread(target=server,args=(DECODE_PORT, decoder,))
        _decoder_thread.start()

        _encoder_thread.join()
        _decoder_thread.join()
    except Exception as e:
        logger.info(e)

if __name__ == "__main__":
    main()