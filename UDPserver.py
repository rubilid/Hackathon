import struct
import socket
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
while True:
    # todo: send offer once in a second

    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

    message = bytesAddressPair[0]

    address = bytesAddressPair[1]
    while True:
        UDPServerSocket.sendto(structured_msg, address)
        time.sleep(1)


    clientMsg = "Message from Client:{}".format(message)
    clientIP = "Client IP Address:{}".format(address)

    print(clientMsg)
    print(clientIP)

    # Sending a reply to client

    UDPServerSocket.sendto(bytesToSend, address)