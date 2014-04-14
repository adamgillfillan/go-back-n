import socket               # Import socket module
import pickle
from collections import namedtuple

PKT_SIZE = 1024
DATA_SIZE = 64
ZERO_FIELD = 0
ACK_TYPE = 1010101010101010

data_pkt = namedtuple('data_pkt', 'seq_num checksum data_type data')
ack_pkt = namedtuple('ack_pkt', 'seq_num zero_field data_type')


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)         # Create a socket object
    host = socket.gethostname()  # Get local machine name
    port = 7735                 # Reserve a port for your service.
    s.bind((host, port))         # Bind to the port

    while True:
        data, addr = s.recvfrom(1000000)
        data = pickle.loads(data)
        print("Data: ", data)
        seq_num, checksum, data_type, message = data[0], data[1], data[2], data[3]
        print('Sequence number:', seq_num, '\nChecksum:', checksum, '\nData type:', bin(data_type), '\nMessage:', message)


if __name__ == "__main__":
    main()