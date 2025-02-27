import socket
import random

class ReliableUDPServer:
    def __init__(self, ip, port, loss_prob=0.1):
        self.ip = ip
        self.port = port
        self.loss_prob = loss_prob
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.expected_seq_num = 0

    def receive_packet(self):
        packet, addr = self.sock.recvfrom(1024)
        if random.random() > self.loss_prob:
            seq_num, data = packet.decode().split(":", 1)
            seq_num = int(seq_num)
            if seq_num == self.expected_seq_num:
                self.expected_seq_num += 1
                self.sock.sendto(str(self.expected_seq_num - 1).encode(), addr)
            else:
                self.sock.sendto(str(self.expected_seq_num - 1).encode(), addr)
        else:
            print(f"Packet lost: {packet}")

if __name__ == "__main__":
    server = ReliableUDPServer("127.0.0.1", 12345, loss_prob=0.1)
    while True:
        server.receive_packet()