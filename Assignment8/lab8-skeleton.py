# Netwerken en Systeembeveiliging
# Lab 8 - Distributed Sensor Network
# Author(s) and student ID(s): Inge Becht 6093906
# Group: Awesome Inge
# Date:
import sys
import struct
import random
import select
from gui import MainWindow
from sensor import *
from socket import *
import time

# Sends a ping message to MCAST_GRP

def send_ping(socket):
    encripted_message = message_encode(MSG_PING )
    socket.sendto(encripted_message, (MCAST_GRP, MCAST_PORT))
    

def socket_subscribe_mcast(sock, ip):
    """
    Subscribes a socket to multicast.
    """
    mreq = struct.pack("4sl", inet_aton(ip), INADDR_ANY)
    sock.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)

# Handles depending on the type of message received
def handle_message(message, address):
    #First decript the message
    decripted_message = message_decode(message)
    if decripted_message[0] == MSG_PING:
        print "Receiev a ping message"
 

def main(argv):
    """
    Program entry point.
    """
    ## Create the multicast listener socket and suscribe to multicast.
    mcast = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    socket_subscribe_mcast(mcast, MCAST_GRP)
    # Bind it to the multicast address.
    # NOTE: You may have to bind to localhost or '' instead of MCAST_GRP
    # depending on your operating system.
    # ALSO: In the lab room change the port to MCAST_PORT + group number
    # so that messages rom different groups do not interfere.
    # When you hand in your code in it must listen on (MCAST_GRP, MCAST_PORT).


    # Make resuable
    mcast.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    mcast.bind((MCAST_GRP, MCAST_PORT))


    ## Create the peer-to-peer socket.
    peer = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    # Set the socket multicast TTL so it can send multicast messages.
    peer.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 2)
    # Bind the socket to a random port.
    peer.bind(('', INADDR_ANY))

    # TODO: Make global and no duplicate values between nodes
    x = random.randint(0, 99)    
    y = random.randint(0, 99)

    value = random.randint(0, 259898)

    ## This is the event loop.
    window = MainWindow()

    # Show information of newly connected node
    ip_port = "IP:Port = " + str(MCAST_GRP) + ":" + str(INADDR_ANY)
    window.writeln(ip_port)
    window.writeln("position = (" + str(x) + ", " + str(y) + ")")
    window.writeln("sensor value = " + str(value))

    # Send ping to all other users and start clock
    send_ping(peer)

    start = time.time()
    
    # Input from select
    input = [mcast, peer]

    while window.update():

        # In case 5 seconds have passed resend ping message
        if (time.time() - start > PING_PERIOD):
            send_ping(peer)
            start = time.time()
        pass

        descriptors, _, _ = select.select(input, [], [])
        
        for descriptor in descriptors:
            # Receive the message from every descriptor
            message, address = descriptor.recvfrom(1024)
            print message
            print "address"
            print address
            handle_message(message, address)
            
            

    

if __name__ == '__main__':
    sys.exit(main(sys.argv))
