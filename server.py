import struct
from socket import *
import threading
from threading import Timer
import time
# import scapy
from random import randrange
import select
from termcolor import colored


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


# global
clients_counter = -1  # will be initialized to 0 in the server
lock = threading.Lock()  # use for dealing with clients_counter

teamPort = 2140
# serverIp = "127.0.0.1"
serverIp = gethostbyname(gethostname())
# serverIp = "172.18.0.140"
localPort = 13117
bufferSize = 1024
msg_magic_cookie = 0xabcddcba
msg_type = 0x2
msg_server_port = teamPort
structured_msg = struct.pack(
    'IBH', msg_magic_cookie, msg_type, msg_server_port)

while True:
    try:
        # Create a datagram socket
        UDPServerSocket = socket(AF_INET, SOCK_DGRAM)
        UDPServerSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        UDPServerSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        # Bind to address and ip
        UDPServerSocket.bind((serverIp, localPort))
        break
    except Exception as e:
        print(str(bcolors.FAIL) + str(e) + str(bcolors.ENDC))
        continue

print(str(bcolors.OKGREEN) + "Server started, listening on IP address " +
      serverIp + str(bcolors.ENDC))


# this class represents a Offer Sending Thread.
# purpose: sending offer announcements once in a second
class OfferSendingThread(threading.Thread):
    def __init__(self, server_socket, address, msg_magic_cookie, msg_type, teamPort, localPort):
        threading.Thread.__init__(self)
        self.structured_msg = struct.pack(
            'IBH', msg_magic_cookie, msg_type, teamPort)
        self.server_socket = server_socket
        self.local_port = localPort

    def run(self):
        while True:
            UDPServerSocket.sendto(self.structured_msg,
                                   ('<broadcast>', self.local_port))
            time.sleep(1)


# this class represents a Game Welcoming Thread.
# purpose: sending welcome messages
class GameWelcomingThread(threading.Thread):
    def __init__(self, connection_socket, addr, client_team_name, other_team_name, question):
        threading.Thread.__init__(self)
        self.connection_socket = connection_socket
        self.addr = addr
        self.client_team_name = client_team_name
        self.other_team_name = other_team_name
        self.question = question

    def run(self):
        welcome_msg = "Welcome to Quick Maths.\n" \
                      "Player 1: " + self.client_team_name + \
                      "Player 2: " + self.other_team_name + \
                      "==\n" \
                      "Please answer the following question as fast as you can:\n" + self.question + '\n'
        try:
            self.connection_socket.send(str(welcome_msg).encode())
        except Exception as e:
            # print(colored('hello', 'red'))
            print(str(bcolors.FAIL) + str(e) + str(bcolors.ENDC))


# this class represents a Game Starter Thread.
# purpose: start and manage a game
class GameStarter():
    def __init__(self, players_addresses):
        self.players_addresses = players_addresses
        self.questions_bank = [('How much is 1^0 - 0^1 ?', '1'),
                               ('What is the LSB in binary representation of 2*4?', '0'),
                               ('x is the smallest prime number which is bigger than 3. x = ?', '5'),
                               ('x = 2022-1. What is the tens digits of x?', '2'),
                               ('How much is 5%2?', '1'),
                               ('What is the median of (1, 1, 3) ?', '1'),
                               ('How much is 1^(-1) ?', '1'),
                               ('How much is 3^2 ?', '9')]

    def draw(self, res_msg):
        res_msg += "Draw!"
        print(res_msg)
        players_addresses[0][0].send(str(res_msg).encode())
        players_addresses[1][0].send(str(res_msg).encode())

    def decide_game_result(self, answer1, answer2, client1name, client2name, correct_answer):
        res_msg = "Game over!\n" + "The correct answer was " + correct_answer + "!\n\n"
        if answer1 == '' and answer2 == '':
            res_msg += "Draw!"
            return res_msg
        elif answer1 != '':
            if answer1 == correct_answer:
                res_msg += "Congratulations to the winner: " + client1name
            else:
                res_msg += "Congratulations to the winner: " + client2name
        elif answer2 != '':
            if answer2 == correct_answer:
                res_msg += "Congratulations to the winner: " + client2name
            else:
                res_msg += "Congratulations to the winner: " + client1name

        return res_msg

    # players addresses is of the form: (connection_socket, addr, client_team_name)
    def start_game(self):
        # randomizing a question
        question_id = randrange(len(self.questions_bank))
        question = self.questions_bank[question_id][0]
        answer = self.questions_bank[question_id][1]
        players_addresses = self.players_addresses

        gameThread1 = GameWelcomingThread(players_addresses[0][0], players_addresses[0][1], players_addresses[0][2],
                                          players_addresses[1][2], question)
        gameThread2 = GameWelcomingThread(players_addresses[1][0], players_addresses[1][1], players_addresses[1][2],
                                          players_addresses[0][2], question)
        gameThread1.start()
        gameThread2.start()

        timeout = 10
        reads, _, _ = select.select(
            [players_addresses[0][0], players_addresses[1][0]], [], [], timeout)
        answer1 = ''
        answer2 = ''
        if len(reads) > 0:
            if reads[0] == players_addresses[0][0]:
                answer1 = players_addresses[0][0].recv(bufferSize).decode()
            elif reads[0] == players_addresses[1][0]:
                answer2 = players_addresses[1][0].recv(bufferSize).decode()
        res_msg = self.decide_game_result(
            answer1, answer2, players_addresses[0][2], players_addresses[1][2], answer)

        try:
            players_addresses[0][0].send(res_msg.encode())
            players_addresses[1][0].send(res_msg.encode())
        except Exception as e:
            print(str(bcolors.FAIL) + str(e) + str(bcolors.ENDC))

        print(str(bcolors.BOLD) + str(bcolors.OKCYAN) +
              res_msg + str(bcolors.ENDC))


# start sending offer announcements
newthread = OfferSendingThread(
    UDPServerSocket, serverIp, msg_magic_cookie, msg_type, teamPort, localPort)
newthread.start()

while True:
    try:
        server_socket = socket(family=AF_INET, type=SOCK_STREAM)
        server_socket.bind(('', teamPort))
        server_socket.listen()
        break
    except Exception as e:
        print(str(bcolors.FAIL) + str(e) + str(bcolors.ENDC))
        continue

while True:
    lock.acquire()
    count = globals()
    count['clients_counter'] = 0
    lock.release()
    players_addresses = []

    while True:
        lock.acquire()
        count = globals()
        if count['clients_counter'] >= 2:
            lock.release()
            break
        lock.release()
        connection_socket, addr = server_socket.accept()
        try:
            client_team_name = connection_socket.recv(bufferSize).decode()
        except Exception as e:
            print(str(bcolors.FAIL) + str(e) + str(bcolors.ENDC))
            continue
        print(client_team_name)
        lock.acquire()
        count = globals()
        count['clients_counter'] += 1
        players_addresses.append((connection_socket, addr, client_team_name))
        lock.release()
    time.sleep(2)
    game_starter = GameStarter(players_addresses)
    try:
        game_starter.start_game()
    except Exception as e:
        print(str(bcolors.FAIL) + str(e) + str(bcolors.ENDC))
        continue

    time.sleep(2)
