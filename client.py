import socket
import time
import random

class ReliableUDPClient:
    def __init__(self, server_ip, server_port, window_size=10, timeout=2):
        self.server_ip = server_ip
        self.server_port = server_port
        self.window_size = window_size
        self.timeout = timeout
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(self.timeout)
        self.base = 0
        self.next_seq_num = 0
        self.cwnd = 1
        self.ssthresh = 64
        self.packets = {}
        self.acks_received = {}

    def send_packet(self, seq_num, data):
        packet = f"{seq_num}:{data}".encode()
        self.sock.sendto(packet, (self.server_ip, self.server_port))
        self.packets[seq_num] = (time.time(), packet)

    def receive_ack(self):
        try:
            ack, _ = self.sock.recvfrom(1024)
            ack_num = int(ack.decode())
            self.acks_received[ack_num] = True
            while self.base in self.acks_received:
                del self.packets[self.base]
                del self.acks_received[self.base]
                self.base += 1
            if self.base == self.next_seq_num:
                self.cwnd = min(self.cwnd * 2, self.ssthresh) if self.cwnd < self.ssthresh else self.cwnd + 1
            else:
                self.cwnd = max(self.cwnd // 2, 1)
                self.ssthresh = self.cwnd
        except socket.timeout:
            self.cwnd = max(self.cwnd // 2, 1)
            self.ssthresh = self.cwnd
            for seq_num in range(self.base, self.next_seq_num):
                if seq_num in self.packets:
                    self.sock.sendto(self.packets[seq_num][1], (self.server_ip, self.server_port))

    def send_data(self, data):
        data_size = len(data)
        num_packets = (data_size // 1024) + (1 if data_size % 1024 != 0 else 0)
        for i in range(num_packets):
            packet_data = data[i*1024:(i+1)*1024]
            while self.next_seq_num < self.base + self.cwnd:
                self.send_packet(self.next_seq_num, packet_data)
                self.next_seq_num += 1
            self.receive_ack()

if __name__ == "__main__":
    client = ReliableUDPClient("127.0.0.1", 12345)
    data = b"a" * 1000000  
    client.send_data(data)