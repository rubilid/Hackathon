class Packet:
    def __init__(self, prefix, msg_type, server_port):
        self.prefix = prefix
        self.msg_type = msg_type
        self.server_port = server_port
