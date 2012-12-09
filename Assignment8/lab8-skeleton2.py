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
    #First decript the message
    decripted_message = message_decode(message)
   # print("Message")
   # print(decripted_message[0])
    
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
        recv_echo(peer, decripted_message, address)

    # remove sender of echoreply when still in the peerlist 
    if decripted_message[0] == MSG_ECHO_REPLY:
        handle_echo_reply(decripted_message, address)

# Handling an incoming echo_reply
def handle_echo_reply(decripted_message, address):
    global size
    global father
    global size_wave
    # This should always be the case
    if address in peerlist:
        peerlist.remove(address)
    # If it is an OP_SIZE message add the size
    if(decripted_message[4] == OP_SIZE):
        print "Got message from ",
        print address
        print "size is now:",
        size += decripted_message[5]
        print size

    # All peers have send an echo reply
    if len(peerlist) == 0:
        # If we are the initiatorend the wave
        if(x == decripted_message[2][0] and y == decripted_message[2][1]):
            window.writeln("Wave ended")

            # In case of size request print size
            if size_wave:
                size += 1
                window.writeln("size of network is: " + str(size))
                # Make size_wave false
                size_wave = False
                size = 0
            print "-----------------------"

        else:
            # Send echo reply to father, with or without OP_SIZE
            if decripted_message[4] == OP_SIZE:
                send_echo_reply_size(peer, father, decripted_message, size + 1)
                size = 0
            else:
                send_echo_reply(peer, father, decripted_message)
            father = (-1, -1)

	
# sends message in wave to neighbors except father (got message from)
def send_echo(peer, msg, option):
    global peerlist 
    global father
    peerlist = []
    msg = message_encode(MSG_ECHO, msg[1], msg[2], (0,0), option, 0)
    for (neighbor, address) in neighbors:
        if address != father:
            peer.sendto(msg, address)
            peerlist.append(address)

# Handle actions in case of receiving an echo
def recv_echo(peer, msg, address):
    global echoMsg
    global father

    # when 1 neighbor send echo reply (3
    if len(neighbors) is 1 and echoMsg[0] is not msg[1] and echoMsg[1] is not msg[2]:

        # Father is in this case the sender
        father = address
        if (msg[4] == OP_SIZE):
            send_echo_reply_size(peer, father,  msg, 1)
        else:
            send_echo_reply(peer, father, msg)
        father =(-1, -1)

    # received echo message for the first time 
     # send through and add peer to peerlist
    elif echoMsg[0] != msg[1] or echoMsg[1] != msg[2]:
        echoMsg = (msg[1], msg[2])
        father = address
        if(msg[4] == OP_SIZE):
            send_echo(peer, msg, OP_SIZE)
        else:
            send_echo(peer, msg, OP_NOOP)

	# Received echo message for the second time (4
    elif echoMsg[0] == msg[1] and echoMsg[1] == msg[2]:
        #FIXME
        if(msg[4] == OP_SIZE):
            print "send echo reply. (Got OP_SIZE message for second time)"
            send_echo_reply_size(peer, address, msg, 0)
        else:
            print "send echo reply. (Got OP_NOOP message for second time)"
            send_echo_reply(peer, address, msg)
        #print "RESET FATHER"
        #father = (-1, -1)
    else:
        print "You shouldn't be here!"
        
# Sends an echo reply message with op = OP_SIZE
def send_echo_reply_size(peer,address,  msg, size):
    encripted_msg = message_encode(MSG_ECHO_REPLY,msg[1], msg[2],(-1,-1),
            OP_SIZE, size)
    peer.sendto(encripted_msg, address)

# Sends an echo reply message
def send_echo_reply(peer, address, msg):
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

    # size_wave is True in case a wave is ongoing that calculates size
    global size_wave
    size_wave = False

    #last received echo message
    global echoMsg
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

    global peerlist
    peerlist = []

    # TODO: Make global and no duplicate values between nodes
    global x 
    #x = random.randint(0, 10)    
    global y
    #y = random.randint(0, 10)
    x = int(argv[1])
    y = int(argv[2])

    global value
    value = random.randint(0, 259898)

    global size 
    size = 0

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

    # Find ip and port number
    #TODO find ip address
    #peer.connect(('google.com', 0))
    ip, port = peer.getsockname()


    global window
    ## This is the event loop.
    window = MainWindow()

    print( (x,y))

    # Show information of newly connected node TODO: Display Local IP
    ip_port = "IP:Port = " + str(ip) + ":" + str(port)
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
            #print( message_decode(message))
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
            size_wave = False
            waveSeqNr += 1
            window.writeln("Starting wave...")
            msg = MSG_ECHO, waveSeqNr, (x,y), (-1, -1), OP_NOOP, 0 
            # Send wave message to all numbers 1)
            send_echo(peer, msg, OP_NOOP)

        # Initiatie wave with size op
        elif(command == "size" ):
            size_wave = True
            # Make sure start with size = 0
            size = 0
            waveSeqNr += 1
            window.writeln("Starting wave to get size...")
            msg = MSG_ECHO, waveSeqNr, (x,y), (-1, -1), OP_NOOP, 0 
            # Send wave message to all numbers 1)
            send_echo(peer, msg, OP_SIZE)

		# If now input than pass
        elif(command == ""):
            pass
        else:
            window.writeln("\"" + command + "\" is not a valid command")

if __name__ == '__main__':
    sys.exit(main(sys.argv))
