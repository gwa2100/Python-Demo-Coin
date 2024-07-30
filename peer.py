from cointest import STD_PORT


class Peer:
    def __init__(self, p_peer_ip):
        self.address = p_peer_ip
        self.block_height = -1
        self.last_contact = -1

    def check_alive(self):
        message = "cointest|R5"
        self.send_udp_message(self.address, STD_PORT, message.encode("utf-8"))