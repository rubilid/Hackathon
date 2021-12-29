import struct
import socket
# import getch
import sys
import threading
import time

# global var
is_game_over = False


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class SendFromClientThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        answer = sys.stdin.readline()[0]
        print('\n')
        global is_game_over
        if not is_game_over:
            TCPClientSocket.send(str.encode(answer))


class ReadFromServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        game_res_msg = TCPClientSocket.recv(bufferSize).decode()
        global is_game_over
        is_game_over = True
        print(game_res_msg)


client_team_name = "Matilda\n"
print(str(bcolors.BOLD) + str(bcolors.OKGREEN) + 'Client started, listening for offer requests...' + str(bcolors.ENDC))
bufferSize = 1024
# Create a UDP socket at client side
try:
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    # Send to server using created UDP socket
    UDPClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDPClientSocket.bind(('', 13117))
except Exception as e:
    print(str(bcolors.FAIL) + str(e) + str(bcolors.ENDC))


while True:
    is_game_over = False
    try:
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)
    except Exception as e:
        print(str(bcolors.FAIL) + str(e) + str(bcolors.ENDC))
    # if str((msgFromServer[1][0])) != '172.18.0.140':
    #     continue

    msg = msgFromServer[0]
    # unpacked_msg contains the data for connecting server:
    # cookie prefix, msg type and TCP port
    unpacked_msg = struct.unpack('IBH', msg)

    if unpacked_msg[0] != 2882395322:
        print(str(bcolors.BOLD) + str(bcolors.WARNING) + "Received a message which does not start with magic cookie." + str(bcolors.ENDC))
        print(str(bcolors.BOLD) + str(bcolors.WARNING) + "Client exiting."+ str(bcolors.ENDC))
        continue
        # exit(0)

    print(str(bcolors.OKBLUE) + "Received offer from " + str(msgFromServer[1]) + " attempting to connect..." + str(bcolors.ENDC))
    structured_msg = str.encode(client_team_name)
    welcome_game_msg = ''
    try:
        TCPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCPClientSocket.connect((msgFromServer[1][0], unpacked_msg[2]))
        TCPClientSocket.send(structured_msg)

        # game starts:
        welcome_game_msg = TCPClientSocket.recv(bufferSize).decode()
    except Exception as e:
        print(str(bcolors.FAIL) + str(e) + str(bcolors.ENDC))

    print(str(bcolors.OKBLUE) + welcome_game_msg + str(bcolors.ENDC))

    try:
        sendFromClientThread = SendFromClientThread()
        readFromServerThread = ReadFromServerThread()
        readFromServerThread.start()
        sendFromClientThread.start()
        readFromServerThread.join()
        TCPClientSocket.close()
    except Exception as e:
        print(str(bcolors.FAIL) + str(e) + str(bcolors.ENDC))
    time.sleep(5)