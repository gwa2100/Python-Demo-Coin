import logging
import socket

from helperfunctions import is_ip_private, get_wan_ip_address, get_lan_ip_address, get_current_timestamp
from transactionqueue import TransactionQueue


class NetworkHandler:
    def __init__(self, p_socket):
        self.seed_ip_list = ["192.168.86.29"]
        self.seed_port = 30003
        self.target_ip_list = []
        self.validated_peers = ["192.168.86.29"]
        self.target_port = 30003
        self.peer_block_heights = {}
        self.transaction_queue = []
        self.sock = p_socket
    def get_block_height(self):
        return 199

    def purge_none_hosts(self):
        self.target_ip_list = list(filter(None, self.target_ip_list))
        self.validated_peers = list(filter(None, self.validated_peers))

    def get_peers_from_seeds(self):
        for seeder in self.seed_ip_list:
            self.target_ip_list.append(self.get_peers_from_target(seeder, self.seed_port))
        self.purge_none_hosts()

    def get_peers_from_peers(self):
        for peer in self.validated_peers:
            self.target_ip_list.append(self.get_peers_from_target(peer, self.target_port))
        self.purge_none_hosts()

    def get_peer_block_height(self, p_peer_ip):
        self.send_udp_message(p_peer_ip, self.target_port, b"cointest|R4")

    def add_peer(self, p_peer_ip):
        if p_peer_ip == get_lan_ip_address() or p_peer_ip == get_wan_ip_address():
            logging.info(get_current_timestamp() + "| add_peer: Dropped peer reference to self.")
            return False
        self.check_peer_valid(p_peer_ip)
        if p_peer_ip in self.validated_peers:
            logging.info(get_current_timestamp() + "| add_peer: Peer " + p_peer_ip + " Already Validated")
            return False
        if p_peer_ip in self.target_ip_list:
            logging.warning(get_current_timestamp() + "| add_peer: Peer " + p_peer_ip + " Already Awaiting Validation")
            return False
        self.target_ip_list.append(p_peer_ip)
        return True

    def check_peer_valid(self, p_peer_ip):
        if p_peer_ip in self.validated_peers:
            logging.info(get_current_timestamp() + "| add_peer: Peer " + p_peer_ip + " Already Validated")
            return True

        response = self.send_udp_message(p_peer_ip, self.target_port, "cointest|R3")
        if response:
            self.mark_peer_valid(p_peer_ip)
        else:
            logging.warning(get_current_timestamp() + "| chec_peer_valid: Peer " + p_peer_ip + " is Invalid")
            logging.warning(p_peer_ip + " was found to be invalid.")
            try:
                self.target_ip_list.remove(p_peer_ip)
            except ValueError:
                pass
            return False

    def mark_peer_valid(self, p_peer_ip):
        if p_peer_ip in self.validated_peers:
            logging.info(get_current_timestamp() + "| add_peer: Peer " + p_peer_ip + " Already Validated")
            return False
        if p_peer_ip in self.target_ip_list:
            self.target_ip_list.remove(p_peer_ip)
        self.validated_peers.append(p_peer_ip)
        logging.info(get_current_timestamp() + "| add_peer: Peer " + p_peer_ip + "Validated")
        return True

    #Expect to send a request (R1) to the target IP to get back a list of peers that the target knows of.
    #Format of return will be "cointest|R1R|111.222.333.444,9.8.7.6,5.4.3.2"  where the last comma
    #   delimited field is a list of peer IPs.
    def get_peers_from_target(self, p_target_ip, p_target_port):
        # Create a UDP socket
        sock = self.sock
        #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        server_address = p_target_ip, p_target_port
        message = b'cointest|R1'
        self.send_udp_message(p_target_ip, p_target_port, message)

        # try:
        #     # Send data
        #     print('sending {!r}'.format(message))
        #     print(server_address[0])
        #     sent = sock.sendto(message, server_address)
        #
        #     # Receive response
        #     print('waiting to receive')
        #     data, server = sock.recvfrom(4096)
        #     print('received {!r}'.format(data))
        #
        # except socket.error:
        #     pass


    # This will send out the transactions to all known peers.
    # Format: cointest|R2|transactionhash:fromacct:toacct:amount:bonus,...
    # Below is the target format...at this time representation is incorrect as it is string format.
    # Limit is 65000 bytes for a package.  10B|2B|512b:512b:512b:32b:32b(+5Bytes spacing)
    # one byte is in between transactions.
    # Preamble size: 96 bits
    # Spacing per transaction: 40 bits
    # Transaction size: 1600 bits
    # Transaction with Spacing: 1640 bits
    # Max Transactions Per Package: 520000 bits or 317 transactions
    # Expects packet back of: cointest|R2R|numberoftransactions
    def send_transaction_queue_to_peers(self, p_trans_que: TransactionQueue, p_send_to = -1):
        if p_send_to == -1:
            p_send_to = self.validated_peers
        if len(p_trans_que.transaction_queue) > 0:
            package = b"cointest|R2|"
            for transaction in p_trans_que.transaction_queue:
                transaction_data =  transaction.get_transaction_list()
                item = ""
                for element in transaction_data:
                    item += element + ","
                item = item[0:-1]
                item += ";"
                package += item

            for peer in p_send_to:
                return_data = self.send_wait_for_response(peer, self.target_port, package, "R2R", "none")

    def process_peer_messages(self):
        data = b''
        address = ''
        try:
            data, address = self.sock.recvfrom(10000)
        except socket.error:
            pass
        finally:
            data = data.decode("utf-8")
            if len(data) > 1:
                if data.split("|")[0] == "cointest":
                    logging.debug(get_current_timestamp() + "| Received Valid Message from " + address[0])
                    # HANDLE PEER REQUEST
                    if "R1" == data.split("|")[1]:
                        logging.debug(get_current_timestamp() + "| Handling R1")
                        message = "cointest|R1R|"
                        peers = 0
                        for peer in self.validated_peers:
                            if peer == address[0]:
                                continue
                            if is_ip_private(address[0]):
                                message += peer + ","
                                peers += 1
                            else:
                                if not is_ip_private(peer):
                                    message += peer + ","
                                    peers += 1
                        message = message[:-1]
                        if peers > 0:
                            self.send_udp_message(address[0], address[1], message.encode("utf-8"))
                            logging.debug(get_current_timestamp() + "| Sent " + message + " to " + address[0])
                        else:
                            logging.debug(get_current_timestamp() + "| No Peers to send to " + address[0])

                    # HANDLE PEER REQUEST RESPONSE
                    if data.split("|")[1] == "R1R":
                        logging.debug(get_current_timestamp() + "| Handling R1R")
                        self.mark_peer_valid(address[0])
                        host_list = data.split("|")[2].split(",")
                        for host in host_list:
                            self.add_peer(host)

                    # HANDLE TRANSACTION SEND RESPONSE
                    if data.split("|")[1] == "R2":
                        logging.debug(get_current_timestamp() + "| Handling R2")
                        self.send_transaction_queue_to_peers(self.transaction_queue, address[0])

                    # HANDLE TRANSACTION SEND RESPONSE
                    if data.split("|")[1] == "R2R":
                        logging.debug(get_current_timestamp() + "| Handling R2R")
                        if int(data.split("|")[2]) > 0:
                            logging.debug(get_current_timestamp() + "| received transaction len from " + address[0])

                    # HANDLE PEER VALID REQUEST
                    if data.split("|")[1] == "R3":
                        logging.debug(get_current_timestamp() + "| Handling R3")
                        message = "cointest|R3R"
                        self.send_udp_message(address[0], address[1], message.encode("utf-8"))
                        logging.debug(get_current_timestamp() + "| Sent " + message + " to " + address[0])

                    # HANDLE PEER VALID REQUEST RESPONSE
                    if data.split("|")[1] == "R3R":
                        logging.debug(get_current_timestamp() + "| Handling R3R")
                        self.mark_peer_valid(address[0])

                    # HANDLE BLOCK HEIGHT REQUEST
                    if data.split("|")[1] == "R4":
                        logging.debug(get_current_timestamp() + "| Handling R4")
                        message = "cointest|R4R|" + str(self.get_block_height())
                        self.send_udp_message(address[0], address[1], message.encode("utf-8"))
                        logging.debug(get_current_timestamp() + "| Sent " + message + " to " + address[0])

                    # HANDLE BLOCK HEIGHT REQUEST RESPONSE
                    if data.split("|")[1] == "R4R":
                        logging.debug(get_current_timestamp() + "| Handling R4R")
                        block_height = int(data.split("|")[2])
                        self.peer_block_heights[address[0]] = block_height

                    # Since it was a valid host, add them to valid peers
                    self.mark_peer_valid(address[0])
                    logging.debug(get_current_timestamp() + "| Marked " + address[0] + " as validated peer.")
                else:
                    logging.warning("RECEIVED BAD PACKET FROM: " + address[0])
            else:
                return False

    def send_wait_for_response(self, p_target_ip, p_port, p_message, p_expected_response_type, p_expected_response):
        print("PLEASE REMOVE SEND_WAIT_FOR_RESPONSE CALL ---DEPRECATED---")
        logging.critical("REMOVE send_wait_for_response (DEPRECATED)")
        # Create a UDP socket
        sock = self.sock

        server_address = (p_target_ip, p_port)
        message = p_message
        try:

            # Send data
            logging.debug(get_current_timestamp() + "| Sending " + message + " to " + server_address[0])
            sent = sock.sendto(message, server_address)

            # Receive response
            print('waiting to receive1')
            data, server = sock.recvfrom(4096)
            print('received {!r}'.format(data))
        except socket.error:
            pass
        finally:
            if data.split("|")[0] == "cointest" and data.split("|")[1] == p_expected_response_type:
                if p_expected_response == "none" or p_expected_response == data.split("|")[2]:
                    return data
            else:
                print("IMPROPER DATA RECEIVED FROM HOST")
                return False

    def send_udp_message(self, p_target_ip, p_port, p_message):
        # Create a UDP socket
        sock = self.sock

        l_server_address = p_target_ip, p_port
        message = p_message
        if isinstance(message, str):
            message = message.encode('utf-8')
        try:
            # Send data
            logging.debug(get_current_timestamp() + "| Sending " + message.decode('utf-8') + " to " + l_server_address[0])
            sent = sock.sendto(message, l_server_address)

        except:
            logging.error(get_current_timestamp() + "| Failed Sending " + message.decode('utf-8') + " to " + l_server_address[0])
            pass