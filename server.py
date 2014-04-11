import socket               # Import socket module
import sys
from struct import *
import pickle
from collections import namedtuple

PKT_SIZE = 1024
DATA_SIZE = 64
ZERO_FIELD = 0
ACK_TYPE = 0b1010101010101010

data_pkt = namedtuple('data_pkt', 'seq_num checksum data_type data')
ack_pkt = namedtuple('ack_pkt','seq_num zero_field data_type')


def main():

    s = socket.socket()         # Create a socket object
    host = socket.gethostname() # Get local machine name
    port = 12345                # Reserve a port for your service.
    s.bind((host, port))        # Bind to the port

    s.listen(5)                 # Now wait for client connection.

    c, addr = s.accept()     # Establish connection with client.
    print('Got connection from', addr)
        #c.send('Thank you for connecting')
    while True:
        pkt_recv, add = c.recvfrom(PKT_SIZE)
        #seq_num, checksum, data_type, message = unpack('ihh' + str(DATA_SIZE) + 's', pkt_recv)
        my_new_list = pickle.loads(pkt_recv)
        seq_num, checksum, data_type, message = my_new_list[0], my_new_list[1], my_new_list[2], my_new_list[3]

        print('Sequence number:', seq_num, '\nChecksum:', checksum, '\nData type:', bin(data_type), '\nMessage:', message)

    c.close()                # Close the connection

if __name__ == "__main__":
    main()