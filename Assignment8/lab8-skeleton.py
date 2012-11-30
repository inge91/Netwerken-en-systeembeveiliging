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
    # Encrypt message, then send it 
    encripted_message = message_encode(MSG_PING,0, (x,y), (-1,-1))
    socket.sendto(encripted_message, (MCAST_GRP, MCAST_PORT))

# Pong message send via unicast
def send_pong(socket, initiator, address):
    # Encrypt message, then send it back to initiator
    encripted_message = message_encode(MSG_PING,0, initiator, (x,y))
    #send unicast
    socket.sendto(encripted_message, address)
    
# Handles depending on the type of message received
def handle_message(peer, message, address):
    #First decript the message
    decripted_message = message_decode(message)
    print decripted_message
    
    # When receiving message, send pong message in case
    # of being close enough
    if decripted_message[0] == MSG_PING:
        if((x,y) == decripted_message[2]):
            print "These are on the same position!"
            pass
        elif(True):
            print "Received ping message"
            send_pong(peer, decripted_message[2], address)
    if decripted_message[0] == MSG_PONG:
        print "Received a pong message"
        
 
def socket_subscribe_mcast(sock, ip):
    """
    Subscribes a socket to multicast.
    """
    mreq = struct.pack("4sl", inet_aton(ip), INADDR_ANY)
    sock.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)


def main(argv):
    """
    Program entry point.
    """

    # Set some of the global variables
    global neighbors
    neighbors = []

    # TODO: Make global and no duplicate values between nodes
    global x 
    x = random.randint(0, 99)    
    global y
    y = random.randint(0, 99)

    global value
    value = random.randint(0, 259898)

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


    ## This is the event loop.
    window = MainWindow()

    # Show information of newly connected node
    ip_port = "IP:Port = " + str(MCAST_GRP) + ":" + str(INADDR_ANY)
    window.writeln(ip_port)

    window.writeln("position = (" + str(x) + ", " + str(y) + ")")
    window.writeln("sensor value = " + str(value))

    # Send ping to all other users and start clock
    print "Here2"
    send_ping(peer)

    start = time.time()
    
    # Input for select
    input = [mcast, peer]

    peer.setblocking(0)
    mcast.setblocking(0)

    while window.update():
        # In case 5 seconds have passed resend ping message
        if (time.time() - start > PING_PERIOD):
            print "Here"
            send_ping(peer)
            start = time.time()
        
        
        # TODO make select nonblocking
        # Read all incoming messages
        #descriptors, _, _ = select.select(input, [], [])

        #for descriptor in descriptors:
            # Receive the message from every descriptor
        try: 
            message, address = mcast.recvfrom(1024)
        except error:
            pass
        try: 
            message = peer.recv(1024)
        except error:
            pass

        # TODO making gui display list of members and such
            
            

    

if __name__ == '__main__':
    sys.exit(main(sys.argv))
