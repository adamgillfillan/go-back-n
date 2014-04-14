import socket  # Import socket module
import sys
from collections import namedtuple
import pickle

DATA_TYPE = 0b101010101010101
DATA_SIZE = 64   #need to be modified

data_pkt = namedtuple('data_pkt', 'seq_num checksum data_type data')
ack_pkt = namedtuple('ack_pkt', 'seq_num zero_field data_type')


def calculate_checksum(message):
    checksum = 0
    return checksum


def pack_data(message, seq_num):
    pkt = data_pkt(seq_num, calculate_checksum(message), DATA_TYPE, message)
    #packed_pkt = pack('ihh' + str(DATA_SIZE) + 's', pkt.seq_num, pkt.checksum, pkt.data_type, bytes(pkt.data,'utf-8'))
    my_list = [pkt.seq_num, pkt.checksum, pkt.data_type, pkt.data]
    packed_pkt = pickle.dumps(my_list)
    return packed_pkt


def prepare_pkts(file_content):
    pkts_to_send = []
    seq_num = 0
    for item in file_content:   # Every MSS bytes should be packaged into segment Foo
        pkts_to_send.append(pack_data(item, seq_num))
    return pkts_to_send
    #your code here


def send_file(file_content, sock, hostname, port):
    num_pkts_sent = 0
    pkts = prepare_pkts(file_content)
   # print(file_content)

    while num_pkts_sent < len(pkts):
        sock.sendto(pkts[num_pkts_sent], (hostname, port))
        num_pkts_sent += 1
    #your code here


def main():
    N = input("Please enter window size N:>")
    MSS =input("Please enter MSS in Bytes:>")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a socket object
    host = socket.gethostname()  # Get local machine name
    port = 7735  # Reserve a port for your service.

    try:
        test_file = open('test_file.txt', 'r')
        file_content =[]
        while True:
            chunk = test_file.read(int(MSS))  # Read the file MSS bytes each time Foo
            file_content.append(chunk)
            print(chunk)
            if not chunk:
                break
        #print(file_content)
        test_file.close()
    except:
        sys.exit("Failed to open file!")

    send_file(file_content, s, host, port)
    s.close()  # Close the socket when done


if __name__ == "__main__":
    main()


