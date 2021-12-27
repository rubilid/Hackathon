import socket

msgFromClient = "Hello UDP Server"
bytesToSend = str.encode(msgFromClient)
serverAddressPort = ("127.0.0.1", 13117)
bufferSize = 1024
# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# Send to server using created UDP socket
UDPClientSocket.sendto(bytesToSend, serverAddressPort)
msgFromServer = UDPClientSocket.recvfrom(bufferSize)
msg = "Message from Server {}".format(msgFromServer[0])
msg2 = msgFromServer[0]
#
# msgToHex = int(msg2, base=16)
# print("client rcvd hex number: " + hex(msgToHex))
# cookieMask = 0xabcddcba000
# if (msgToHex ^ cookieMask)  == 0:
#     print("cookie format!")
# print("unrecognized format!, " + hex((msgToHex ^ cookieMask)))

print(msg)