import struct
import socket

team_name = "Lin\n"
msgFromClient = "Hello UDP Server"
print('Client started, listening for offer requests...')
bytesToSend = str.encode(msgFromClient)
serverAddressPort = ("127.0.0.1", 13117)
bufferSize = 1024
# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# Send to server using created UDP socket
UDPClientSocket.sendto(bytesToSend, serverAddressPort)
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
TCPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
TCPClientSocket.connect(serverAddressPort)
# sending team name to server
# structured_msg = struct.pack('s', str.encode(team_name))
structured_msg = str.encode(team_name)
TCPClientSocket.send(structured_msg)
