import time
import socket
import logging

#constants
from helperfunctions import get_lan_ip_address, get_peer_list_checksum, get_timestamp_seconds, \
    get_current_timestamp
from networkhandler import NetworkHandler

STD_PORT = 30003


#TODO: Change peers to be tracked using the Peer Objects


#STARTUP
logging.basicConfig(filename='cointest.log', level=logging.DEBUG)
logging.info(get_current_timestamp() + "| CoinTest Started")

# Create a UDP socket
g_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = get_lan_ip_address(), 30003
# Bind the socket to the port
logging.debug(get_current_timestamp() + "|starting up on {} port {}".format(*server_address))
g_sock.bind(server_address)
g_sock.setblocking(0)
logging.debug(get_current_timestamp() + "| Created UDP SOCKET g_sock")


print("\nNetwork Test")
net = NetworkHandler(g_sock)
net.get_peers_from_seeds()
net.get_peers_from_peers()
start_time = int(time.time())
oldpeerchecksum = ''
peerchecksum = ''
latch = False
time_keeper = get_timestamp_seconds()
while True:
    peerchecksum = get_peer_list_checksum(net.validated_peers)
    if oldpeerchecksum != peerchecksum or get_timestamp_seconds() > time_keeper + 15:
        oldpeerchecksum = peerchecksum
        time_keeper = get_timestamp_seconds()
        net.get_peers_from_peers()
        print("=============")
        print("PEER LIST")
        for peer in net.validated_peers:
            logging.debug(get_current_timestamp() + "| Validating Peers")
            try:
                print(peer + "| BH: " + str(net.peer_block_heights[peer]))
            except KeyError:
                print(peer)
        print("=============")
    net.process_peer_messages()

    if int(time.time() - start_time) % 20 == 0 and not latch:
        logging.debug(get_current_timestamp() + "| Getting peercheck block height")
        latch = True
        for peer in net.validated_peers:
            net.get_peer_block_height(peer)
    if int(time.time() - start_time) % 20 and latch:
        logging.debug(get_current_timestamp() + "| Reset peercheck Latch")
        latch = False
g_sock.close()
