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
    print address
    socket.sendto(encripted_message, address)
    
# Handles depending on the type of message received
def handle_message(peer, mcast, message, address):
    #First decript the message
    decripted_message = message_decode(message)
    print decripted_message
    
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
		recv_echo(decripted_message,address)
	if decripted_message[0] == MSG_ECHO_REPLY:
		send_echo_reply()

#wave_seq_nr

# sends message in wave to neighbors except father (got message from)
def send_echo(peer, msg, father):
    msg = sensor.encode(MSG_ECHO,msg[1], msg[2], null, NOOP, 0)
	for (neighbor, address) in neighbors:
		if address is not father:
            peer.sendto(msg, address )


def recv_echo(peer, msg, address):
    # when 1 neighbor send echo reply (3
    if neighbors.length == 1:
        send_echo_reply(msg,address)
    # propagate wave when not done already 4)
    elif echoMsg is not (msg[1], msg[2]):
        global echoMsg
        echoMsg = (msg[1], msg[2])
        send_echo(msg, address)
        # do not propagate wave
    else:
        send_echo_reply(msg,address)

def send_echo_reply(msg):
	sensor.encode(MSG_ECHO_REPLY,msg[1],msg[2],null, NOOP, 0)
	
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
    echoMsg = (0, 0)
    global waveSeqNr
    waveSeqNr = 0
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


    print (x,y)

    # Show information of newly connected node
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
            #Make a move to a new position TODO make smarter
		# Initiate wave
        elif(command == "wave"):
            waveSeqNr += 1
            encripted_message = encode(MSG_ECHO, waveSeqNr, (x,y), (-1, -1), NOOP, 0)
            # Send wave message to all numbers
            for i in neighbors:
                peer.sendto(message, i[1])
		# If now input than pass
        elif(command == ""):
            pass
        else:
            window.writeln("\"" + command + "\" is not a valid command")
        print neighbors

    

if __name__ == '__main__':
    sys.exit(main(sys.argv))
