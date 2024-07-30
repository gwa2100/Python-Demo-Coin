import datetime
import hashlib
import ipaddress
import socket
import time
import urllib.request


def is_ip_private(p_ip_addr):
    return ipaddress.ip_address(p_ip_addr).is_private


def get_wan_ip_address():
    return urllib.request.urlopen('https://ident.me').read().decode('utf8')


def get_lan_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return_name = s.getsockname()[0]
    s.close()
    return return_name


def get_current_time():
    return str(int(time.time()))


def get_peer_list_checksum(p_peerlist):
    peerstring = ""
    for peer in p_peerlist:
        peerstring += peer
    return hashlib.blake2b(peerstring.encode('utf-8')).hexdigest()


def get_timestamp_seconds():
    return int(time.time())


def get_current_timestamp():
    return str(datetime.datetime.now())