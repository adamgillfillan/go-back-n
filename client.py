import socket  # Import socket module
import sys
from collections import namedtuple
import pickle
from _thread import *
import threading
import time

DATA_TYPE = 0b101010101010101
DATA_SIZE = 64   #need to be modified

data_pkt = namedtuple('data_pkt', 'seq_num checksum data_type data')
ack_pkt = namedtuple('ack_pkt', 'seq_num zero_field data_type')
N = 0  # window size
MSS = 0 # maximum segment size
ACK = 0 # ACK received from server.
num_pkts_sent = 0
num_pkts_acked = 0
seq_num = 0
#print(file_content)
#print (N)
window_low = 0
window_high = int(N)-1
total_pkts = 0
RTT = 5
pkts = []


ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP Foo
host = socket.gethostname()
ack_port_num = 62223
ack_socket.bind((host, ack_port_num))


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


def pack_data(message, seq_num):
    pkt = data_pkt(seq_num, calculate_checksum(message), DATA_TYPE, message)
    #packed_pkt = pack('ihh' + str(DATA_SIZE) + 's', pkt.seq_num, pkt.checksum, pkt.data_type, bytes(pkt.data,'utf-8'))
    my_list = [pkt.seq_num, pkt.checksum, pkt.data_type, pkt.data]
    packed_pkt = pickle.dumps(my_list)
    return packed_pkt


def prepare_pkts(file_content, seq_num):
    pkts_to_send = []
    seq_num = 0
    for item in file_content:   # Every MSS bytes should be packaged into segment Foo
        pkts_to_send.append(pack_data(item, seq_num))
        seq_num += 1
    return pkts_to_send
    #your code here

def socket_function(pkts):
    #print (pkts)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a socket object

    # comment this block when ready for command line argument
    # N = input("Please enter window size N:>")
    # MSS = input("Please enter MSS in Bytes:>")
    host = socket.gethostname()  # Get local machine name
    # print("Host:", host)
    port = 7735  # Reserve a port for your service.
    s.sendto(pkts, (host, port))
    s.close()

def timer():
    global pkts
    global window_low
    global window_high
    global total_pkts
    global ACK
    t = threading.Timer(RTT, timer)
    t.start()
    resent_index = window_low  # resent from window_low to window_high
    if ACK == window_low:
        print ("resent begin")
        while resent_index <= window_high and resent_index < total_pkts:
            print ("resent "+ str(resent_index))
            socket_function(pkts[resent_index])
            resent_index += 1
        print("=========")

def send_file(file_content, sock, hostname, port):
    global total_pkts
    total_pkts = len(file_content)
    #print(total_pkts)
    global pkts
    pkts= prepare_pkts(file_content, seq_num)
    global num_pkts_sent
    #send the first window
    while num_pkts_sent < int(N):
       # socket_function(pkts[num_pkts_sent], sock, hostname, port)
        #t = threading.Timer(RTT,socket_function("hello"))
        socket_function(pkts[num_pkts_sent])
        num_pkts_sent += 1
        #data = pickle.loads(ack_socket.recv(1024))
        #print(data[0])
    #deal with the sliding window
    # while num_pkts_sent < total_pkts:
    #     global ACK
    #     ACK = data[0]  # ack_seq
    #     #print(ACK)
    #     global window_low
    #     global window_high
    #     global num_pkts_acked
    #     # print ("total pkts" + str(total_pkts))
    #     if ACK:  # if ACK != null. Foo
    #         if ACK > window_low:
    #             temp_pckts_acked = ACK - window_low
    #             window_high = window_high + ACK - window_low
    #             window_low = ACK
    #             num_pkts_acked += temp_pckts_acked  # Acked # of packages. Foo
    #             # print ("window_high+ "+ str(window_high))
    #             if window_high < total_pkts: # Still have packages to be sent. Foo
    #                 for i in range(min(temp_pckts_acked, total_pkts - window_high-1)): # check how many pkts left to sent. Foo
    #                     #print(num_pkts_sent)
    #                     sock.sendto(pkts[num_pkts_sent], (hostname, port))
    #                     num_pkts_sent += 1
    #                     data = pickle.loads(ack_socket.recv(1024))
    #                     print(data[0])

    # while num_pkts_sent < int(N):
    #     sock.sendto(pkts[num_pkts_sent], (hostname, port))
    #     num_pkts_sent += 1
    #your code here


def ack_listen_thread(sock, host, port):
    global window_high
    global window_low
    global num_pkts_sent
    global num_pkts_acked
    global total_pkts
    while True:
        data = pickle.loads(ack_socket.recv(256))
        print("ACK "+str(data[0]))
        print("Wind_low "+str(window_low))
        print("total"+str(total_pkts))
        print("sent"+str(num_pkts_sent))
        if data[2]=="1010101010101010":  # data[2] is ACK identifier data[0] should be ACK sequence number. Foo
            global ACK
            ACK = data[0]
            #print (ACK)
            if ACK:  # if ACK != null. Foo
                #print("hello"+str(ACK))
                if ACK >= window_low and num_pkts_sent < total_pkts:
                    #print(window_low)
                    temp_pckts_acked = ACK - window_low
                    window_high = window_high + ACK - window_low
                    window_low = ACK
                    num_pkts_acked += temp_pckts_acked  # Acked # of packages. Foo
                    if window_high < total_pkts :  # Still have packages to be sent. Foo
                        for i in range(min(temp_pckts_acked, total_pkts - window_high-1)): # check how many pkts left to sent. Foo
                            #sock.sendto(pkts[8], (host, port))
                            socket_function(pkts[num_pkts_sent])
                            num_pkts_sent += 1
                elif ACK <total_pkts:
                     continue  # for the last windows.
                else:
                    print("Done!")
                    exit()



#     # # add something to listen ACK from server.
#
#


def parse_command_line_arguments():
    host = sys.argv[1]
    port = sys.argv[2]
    file_name = sys.argv[3]
    my_window_size = sys.argv[4]
    my_mss = sys.argv[5]

    return host, int(port), file_name, int(my_window_size), int(my_mss)


def main():
    global N
    global MSS

    # Uncomment this when ready for command line argument
    #host, port, my_test_file, N, MSS = parse_command_line_arguments()
    #adam's host = lil_boss
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a socket object

    # comment this block when ready for command line argument
    N = input("Please enter window size N:>")
    MSS = input("Please enter MSS in Bytes:>")
    host = socket.gethostname()  # Get local machine name
    print("Host:", host)
    port = 7735  # Reserve a port for your service.
    my_test_file = 'test_file.txt'
    # finish comment here

    global window_high
    window_high =  int(N)-1
    try:
        test_file = open(my_test_file, 'r')
        file_content = []
        while True:
            chunk = test_file.read(int(MSS))  # Read the file MSS bytes each time Foo
            file_content.append(chunk)
            #print(chunk)
            if not chunk:
                break
        #print(file_content)
        test_file.close()
    except:
        sys.exit("Failed to open file!")
    # start_new_thread(ack_listen_thread, (s, host, port))
    timer()
    threading.Thread(target=ack_listen_thread, args=(s, host, port)).start()
    threading.Thread(target=send_file, args=(file_content, s, host, port)).start()
    s.close()  # Close the socket when done


if __name__ == "__main__":
    main()


