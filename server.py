import socket               # Import socket module
import pickle
import sys
from collections import namedtuple
import random

PKT_SIZE = 1024
DATA_SIZE = 64
ZERO_FIELD = 0
ACK_TYPE = 1010101010101010

data_pkt = namedtuple('data_pkt', 'seq_num checksum data_type data')
ack_pkt = namedtuple('ack_pkt', 'seq_num zero_field data_type')

ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)         # Create a socket object
host = socket.gethostname()  # Get local machine name
port = 62223                 # Reserve a port for your service.
#ack_socket.bind((host, port))         # Bind to the port


def send_ack(seq_num):
    # ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)         # Create a socket object
    # host = socket.gethostname()  # Get local machine name
    # port = 62223                 # Reserve a port for your service.
    # #ack_socket.bind((host, port))         # Bind to the port
    reply_message = [seq_num, "0000000000000000", "1010101010101010"]
    # print(reply_message)
    ack_socket.sendto(pickle.dumps(reply_message), (host, port))


# Carry bit used in one's combliment
def carry_checksum_addition(num_1, num_2):
    c = num_1 + num_2
    return (c & 0xffff) + (c >> 16)


# Calculate the checksum of the data only. Return True or False
def calculate_checksum(message):
    if (len(message) % 2) != 0:
        message += "0"

    checksum = 0
    for i in range(0, len(message), 2):
        w = ord(message[i]) + (ord(message[i+1]) << 8)
        checksum = carry_checksum_addition(checksum, w)
    return (not checksum) & 0xffff


def parse_command_line_arguments():
    port = sys.argv[1]
    file_name = sys.argv[2]
    prob = sys.argv[3]

    return int(port), file_name, float(prob)


def main():
    #port, output_file, prob_loss = parse_command_line_arguments()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)         # Create a socket object
    host = socket.gethostname()  # Get local machine name
    port = 7735                 # Reserve a port for your service.
    s.bind((host, port))         # Bind to the port
    prob_loss = 0.1
    output_file = 'test_output.txt'
    lost_seq_num = []
    packet_lost = False
    while True:

        data, addr = s.recvfrom(1000000)
        data = pickle.loads(data)
        print("Data: ", data)
        seq_num, checksum, data_type, message = data[0], data[1], data[2], data[3]
        rand_loss = random.random()
        if rand_loss <= prob_loss:
            print("Packet loss, sequence number = ", seq_num)
            packet_lost = True
            if seq_num not in lost_seq_num:
                lost_seq_num.append(seq_num)
        else:
            if checksum != calculate_checksum(message):
                print("Packet dropped, checksum doesn't match!")
            #else:
            elif not packet_lost:
                #if lost_seq_num
                print (seq_num)
                ack_seq = int(seq_num)+1
                print("ACK "+ str(ack_seq))
                send_ack(ack_seq)
                with open(output_file, 'a') as file:
                    file.write(message)
            else:
                if packet_lost and (seq_num == lost_seq_num[0]):
                    packet_lost = False
                    ack_seq = int(seq_num)+1
                    print("ACK "+ str(ack_seq))
                    send_ack(ack_seq)
                    lost_seq_num.remove(seq_num)
                    with open(output_file, 'a') as file:
                        file.write(message)
                else:
                    pass

        #print('Sequence number:', seq_num, '\nChecksum:', checksum, '\nData type:', bin(data_type), '\nMessage:', message)

if __name__ == "__main__":
    main()