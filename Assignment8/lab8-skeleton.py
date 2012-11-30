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

# Pong message send by unicast
def send_pong(socket, initiator, address):
    # Encrypt message, then send it back to initiator
    encripted_message = message_encode(MSG_PING,0, initiator, (x,y))
    #send unicast
    socket.sendto(encripted_message, (address, INADDR_ANY))
    
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
    
    # When receiving message, send pong message in case
    # of being close enough
    if decripted_message[0] == MSG_PING:
        if(True):
            # extract initiator position
            send_pong()
        
 

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
    global x 
    x = random.randint(0, 99)    
    global y
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

    peer.setblocking(0)
    
    i = 0

    while window.update():
        print i
        i+=1

        # In case 5 seconds have passed resend ping message
        if (time.time() - start > PING_PERIOD):
            send_ping(peer)
            start = time.time()
        pass


        # Read all incoming messages
        descriptors, _, _ = select.select(input, [], [])
        
        for descriptor in descriptors:
            print 'a'
            # Receive the message from every descriptor
            message, address = descriptor.recvfrom(1024)
            print message
            print "address"
            print address
            handle_message(message, address)

        # TODO making gui display list of members and such
            
            

    

if __name__ == '__main__':
    sys.exit(main(sys.argv))
