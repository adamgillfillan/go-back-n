import socket               # Import socket module
import pickle
import sys
from collections import namedtuple
import random
import time
import datetime

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
    # if (len(message) % 2) != 0:
    #     message += bytes("0")

    checksum = 0
    for i in range(0, len(message), 2):
        my_message = str(message)
        w = ord(my_message[i]) + (ord(my_message[i+1]) << 8)
        checksum = carry_checksum_addition(checksum, w)
    return (not checksum) & 0xffff



def parse_command_line_arguments():
    port = sys.argv[1]
    file_name = sys.argv[2]
    prob = sys.argv[3]

    return int(port), file_name, float(prob)


def main():
    port, output_file, prob_loss = parse_command_line_arguments()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)         # Create a socket object
    host = socket.gethostname()  # Get local machine name
    #port = 7735                 # Reserve a port for your service.
    s.bind((host, port))         # Bind to the port
    #prob_loss = 0.01
    #dt = str(datetime.time().second)
    #d = random.randrange(0, 1000000)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    #output_file = 'file_'+str(timestr)+'.pdf'
    lost_seq_num = []
    print_message = []
    packet_lost = False
    exp_seq_num = 0
    while True:

        data, addr = s.recvfrom(1000000)
        data = pickle.loads(data)

        seq_num, checksum, data_type, message = data[0], data[1], data[2], data[3]
        #print("Data: ", str(message))
        rand_loss = random.random()

        if rand_loss <= prob_loss:
            print("Packet loss, sequence number = ", seq_num)
            packet_lost = True
            if len(lost_seq_num) == 0:
                lost_seq_num.append(seq_num)
            if len(lost_seq_num) > 0:
                if seq_num not in lost_seq_num and (seq_num>min(lost_seq_num)):
                    lost_seq_num.append(seq_num)
        else:
            if checksum != calculate_checksum(message):
                print("Packet dropped, checksum doesn't match!")
            #else:
            if seq_num == exp_seq_num:
               # print (seq_num)
                ack_seq = int(seq_num)+1
               # print("ACK "+ str(ack_seq))
                send_ack(ack_seq)
                print_message.append(seq_num)
                with open(output_file, 'ab') as file:
                    file.write(message)
                exp_seq_num += 1

        #     elif not packet_lost:
        #         #if lost_seq_num
        #         print (seq_num)
        #         ack_seq = int(seq_num)+1
        #         print("ACK "+ str(ack_seq))
        #         send_ack(ack_seq)
        #         print_message.append(seq_num)
        #         with open(output_file, 'ab') as file:
        #             file.write(message)
        #     else:
        #         print("print meeeeeeeee")
        #         print("Seq_num: ", seq_num)
        #         print("lost_seq_num: ", lost_seq_num)
        #         if packet_lost and (seq_num == min(lost_seq_num)):
        #             print("my_ack--------")
        #             ack_seq = int(seq_num)+1
        #             print("ACK "+ str(ack_seq))
        #             send_ack(ack_seq)
        #             lost_seq_num.remove(seq_num)
        #             print_message.append(seq_num)
        #             with open(output_file, 'ab') as file:
        #                 file.write(message)
        #             if len(lost_seq_num) < 1:
        #                 packet_lost = False
        #         else:
        #             print("I don't this lost:"+str(packet_lost))
        #             print("I don't this seq_num"+str(seq_num))
        #             print("I don't this lost_seq_num",lost_seq_num)
        #             pass
        # if str(ack_seq) == "1455":
        #     for element in print_message:
        #         print(print_message[element])

        #print('Sequence number:', seq_num, '\nChecksum:', checksum, '\nData type:', bin(data_type), '\nMessage:', message)

if __name__ == "__main__":
    main()