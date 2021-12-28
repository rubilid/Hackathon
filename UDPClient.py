import struct
import socket
# from socket import *

team_name = "Lin\n"
msgFromClient = "Hello UDP Server"
print('Client started, listening for offer requests...')
bytesToSend = str.encode(msgFromClient)
serverAddressPort = ("127.0.0.1", 13117)
bufferSize = 1024
# Create a UDP socket at client side
# UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# UDPClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
# UDPClientSocket.bind((serverAddressPort[0], 13117))
# Send to server using created UDP socket
# UDPClientSocket.sendto(bytesToSend, serverAddressPort)
msgFromServer = UDPClientSocket.recvfrom(bufferSize)
msgToPrint = "Message from Server {}".format(msgFromServer[0])
msg = msgFromServer[0]
unpacked_msg = struct.unpack('IBH', msg)
print(unpacked_msg)

if unpacked_msg[0] != 2882395322:
    print("Received a message which does not start with magic cookie.")
    print("Client exiting.")
    exit(0)

print("Received offer from " + str(msgFromServer[1]) + " attempting to connect...")
# TCPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCPClientSocket.connect((serverAddressPort[0], unpacked_msg[2]))
# TCPClientSocket.connect(TCPClientSocket.getsockname()[0])

print("client rcvd TCP socket: "+ str(TCPClientSocket.getsockname()))
# TCPClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
# TCPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SO_REUSEPORT, 1)
# UDPClientSocket.bind(('', serverAddressPort[1]))
# TCPClientSocket.connect(msgFromServer[1])
# print("tcp connection: " + msgFromServer[1])

# sending team name to server
# structured_msg = struct.pack('s', str.encode(team_name))
structured_msg = str.encode(team_name)
TCPClientSocket.send(structured_msg)
