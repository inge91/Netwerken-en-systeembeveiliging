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
    encripted_message = message_encode(MSG_PONG,0, initiator, (x,y))
    #send unicast
    socket.sendto(encripted_message, address)
    
# Handles depending on the type of message received
def handle_message(peer, mcast, message, address):
    global x
    global y
    global size
    global neighbor_replies
    #First decript the message
    decripted_message = message_decode(message)
    
    # When receiving message, send pong message in case
    # of being close enough
    if decripted_message[0] == MSG_PING:
        init_x, init_y = decripted_message[2]
        if((x,y) == (init_x, init_y)):
            pass
        # FIXME Is this the right way to find the range in a circle
        elif(abs(x - init_x) + abs(y - init_y) < 50):
            send_pong(peer, decripted_message[2], address)
    # In case of pong message add non_initiator to the neighbor list
    if decripted_message[0] == MSG_PONG:
        (non_initiator, address) = (decripted_message[3], address)
        global neighbors
        neighbors.append((non_initiator, address))
	# In case of echo message set sender as father and 
	#		send message to neighbors
    if decripted_message[0] == MSG_ECHO:
        print "received echo"
        print decripted_message[2]
        recv_echo(peer, decripted_message,address)
    # add echo reply to all 
    if decripted_message[0] == MSG_ECHO_REPLY:
        print "Got echo reply"
        neighbor_replies.append(address)
        #FIXME Make check of replies better
        print "Neighbor and replies"
        print neighbor_replies
        print neighbors

        print decripted_message[2]
        print (x,y)
        # In case you are initiater stop the wave by doing nothing
        if(x == decripted_message[2][0] and y == decripted_message[2][1]):
            print "I am initiator"
            size += decripted_message[5]
            if(len(neighbor_replies) == len(neighbors)) :
                print "wave ended"
                size += 1
                if size > 1 :
                    print "size: ",
                    print size
                neighbor_replies = []

            # Send echo reply to father 5)
        else:   
            print "I am not initiator"
            if decripted_message[4] == OP_SIZE:
                print "Received OPSIZE message"
                size += decripted_message[5]
            # Got echo reply from everybody but father
            if(len(neighbor_replies) >= (len(neighbors)-1)):
                global father
                if decripted_message[4] == OP_SIZE:
                    send_echo_reply_size(peer, decripted_message, father, size + 1)
                else:
                    send_echo_reply(peer, decripted_message, father)
                    neighbor_replies = []

# sends message in wave to neighbors except father (got message from)
def send_echo(peer, msg, father):
    print msg[2]
    print "send echo message to ",
    msg = message_encode(MSG_ECHO,msg[1], msg[2], (-1, -1), OP_NOOP, 0)
    for (neighbor, address) in neighbors:
        if address != father:
            print str(address),
            peer.sendto(msg, address) 

# sends message in wave to neighbors except father (got message from) In case of
# op = OP_NOOP
def send_echo_size(peer, msg, father):
    print msg[2]
    print "send echo message to ",
    msg = message_encode(MSG_ECHO,msg[1], msg[2], (-1, -1), OP_SIZE, 0)
    for (neighbor, address) in neighbors:
        if address != father:
            print str(address),
            peer.sendto(msg, address) 

# Handle actions in case of receiving an echo
def recv_echo(peer, msg, address):
    print "Received echo from ",
    print  address 
    global echoMsg
    global neighbor_replies
    global father 
    operation = msg[4]

    # when 1 neighbor send echo reply (3
    if len(neighbors) == 1:
        # Father is in this case the sender
        father = address
        print "Received echo message from my only neighbor send him an echo reply"

        if(msg[4] == OP_SIZE):
            print " OP was OP_SIZE, send reply with size 1"
            send_echo_reply_size(peer, msg, father, 1)
        else:
            send_echo_reply(peer, msg, father)
    # received echo message for the first time 
    elif echoMsg != (msg[1], msg[2]):
        print "First time i receive echo message. Send echo to all other neighbors"
        neighbor_replies = []
        echoMsg = (msg[1], msg[2])
        father = address
        if(msg[4] == OP_SIZE):
            send_echo_size(peer, msg, address)
        else:
            send_echo(peer, msg, address)
    # Received echo message for the second time, NO_OP message to sender
    else:
        print "Send an echo reply to:"
        if(msg[4] == OP_SIZE):
            #FIXME: This should not be a OP_SIZE message
            send_echo_reply_size(peer, msg, address, 0)
        else:
            send_echo_reply(peer, msg, address)

# Sends an echo reply message in case operation is OP_SIZE
def send_echo_reply_size(peer, msg, address, size):
    print "send echo size reply to address " + str(address)
    encripted_msg = message_encode(MSG_ECHO_REPLY,msg[1], msg[2],(-1,-1),
            OP_SIZE, size)
    peer.sendto(encripted_msg, address)

# Sends an echo reply message
def send_echo_reply(peer, msg, address):
    print msg[2]
    print "send echo reply to address " + str(address)
    encripted_msg = message_encode(MSG_ECHO_REPLY,msg[1], msg[2],(-1,-1), OP_NOOP, 0)
    peer.sendto(encripted_msg, address)
	
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

    #last received echo message
    global echoMsg
    global size 
    size = 0

    echoMsg = (0, 0)

    global neighbor_replies
    neighbor_replies = []

    #IP and port of father 
    global father
    father = (-1, -1)

    global waveSeqNr
    waveSeqNr = 0
    # Set some of the global variables
    global neighbors
    neighbors = []
    # TODO: Make global and no duplicate values between nodes
    global x 
    #x = random.randint(0, 99)    
    global y
    #y = random.randint(0, 99)
    x = int(argv[1])
    y = int(argv[2])

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

    port = INADDR_ANY
    # Bind the socket to a random port.
    peer.bind(('', port))

    ## This is the event loop.
    window = MainWindow()

    print (x,y)

    # Show information of newly connected node TODO: Display Local IP
    ip_port = "IP:Port = " + str(MCAST_GRP) + ":" + str(INADDR_ANY)
    window.writeln(ip_port)

    window.writeln("position = (" + str(x) + ", " + str(y) + ")")
    window.writeln("sensor value = " + str(value))

    # Send ping to all other users and start clock
    send_ping(peer)

    start = time.time()
    
    # Input for select
    input = [mcast, peer]

    peer.setblocking(0)
    mcast.setblocking(0)

    while window.update():
        # In case 5 seconds have passed resend ping message
        if ((time.time() - start) > PING_PERIOD):
            neighbors = []
            send_ping(peer)
            start = time.time()
        
        # Read input from mcast and peer
        try: 
            message, address = mcast.recvfrom(1024)
            handle_message(peer, mcast, message, address)
        except error:
            pass
        try: 
            message, address  = peer.recvfrom(1024)
            handle_message(peer, mcast, message, address)
        except error:
            pass
        
        #See if there was GUI input
        command = window.getline()

        # Send a ping to the rest
        if(command == "ping"):
            neighbors = []
            window.writeln("Sending ping over multicast...")
            send_ping(peer)

        # Show the list of neighbors
        elif(command == "list"):
            window.writeln("List of neighbors <(x,y), ip:port>:")
            if neighbors == []:
                window.writeln("No neighbors found")
            for i in neighbors:
                window.writeln(str(i[0]) + ", " + str(i[1][0]) + ":" + str(i[1][1]))

        # Move to a new random position
        elif(command == "move"):
            x = random.randint(0, 99)
            y = random.randint(0, 99)
            window.writeln("New position = " + str((x,y)))

		# Initiate wave
        elif(command == "wave"):
            waveSeqNr += 1
            window.writeln("Starting wave...")
            print (x,y)
            encripted_message = message_encode(MSG_ECHO, waveSeqNr, (x,y), (-1, -1),
                    OP_NOOP, 0) 
            # Send wave message to all neighbors 1)
            for i in neighbors:
                peer.sendto(encripted_message, i[1])
                
        # Initiatie wave with size op
        elif(command == "size" ):
            waveSeqNr += 1
            window.writeln("Starting wave to get size...")
            print (x,y)
            encripted_message = message_encode(MSG_ECHO, waveSeqNr, (x,y), (-1, -1),
                    OP_SIZE, 0) 
            # Send wave message to all neighbors 1)
            for i in neighbors:
                peer.sendto(encripted_message, i[1])

		# If no input than pass
        elif(command == ""):
            pass
        else:
            window.writeln("\"" + command + "\" is not a valid command")


if __name__ == '__main__':
    sys.exit(main(sys.argv))
