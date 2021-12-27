import struct
import socket
import threading
import time
from magicCookie import MagicCookie

serverIp = "127.0.0.1"
localPort = 13117
bufferSize = 1024
msgFromServer = "Hello UDP Client"
# offerMsg = str(MagicCookie(0xabcddcba, 0x2, localPort))
msg_magic_cookie = 0xabcddcba
msg_type = 0x2
msg_server_port = localPort
structured_msg = struct.pack('IBH', msg_magic_cookie, msg_type, msg_server_port)

# bytesToSend = str.encode(offerMsg)
# print(hex(offerMsg))
# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# Bind to address and ip
UDPServerSocket.bind((serverIp, localPort))
print("Server started, listening on IP address " + serverIp)
# Listen for incoming datagrams
threads = []


class OfferSendingThread(threading.Thread):
    def __init__(self, server_socket, address, msg_magic_cookie, msg_type, msg_server_port):
        threading.Thread.__init__(self)
        self.structured_msg = struct.pack('IBH', msg_magic_cookie, msg_type, msg_server_port)
        self.server_socket = server_socket
        self.address = address
        self.msg_magic_cookie = msg_magic_cookie
        self.msg_type = msg_type
        self.msg_server_port = msg_server_port

    def run(self):
        while clients_counter < 2:
            UDPServerSocket.sendto(structured_msg, address)
            print("offer sent!")
            time.sleep(1)


while True:
    clients_counter = 0
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    newthread = OfferSendingThread(UDPServerSocket, address, msg_magic_cookie, msg_type, msg_server_port)
    newthread.start()
    threads.append(newthread)

    clientMsg = "Message from Client:{}".format(message)
    clientIP = "Client IP Address:{}".format(address)

    print(clientMsg)
    print(clientIP)

    # Sending a reply to client

    # UDPServerSocket.sendto(bytesToSend, address)

    for t in threads:
        t.join()
