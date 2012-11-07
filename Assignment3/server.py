#################################################
# Assignment 3: Server in python                #
# By: Inge Becht, 6093906                       #                         
#                                               #    
# Run program by: python server.py              #            
#                                               #
#################################################


import socket
import os
HOST = 'localhost'
PORT = 8888

# Handles the request of the client by returning an approptriate
# reply (404, 501 or 200)
def handle_request(connection):

    # Receive data from buffer
    data = connection.recv(1024)

    # Split the request on whitespace 
    request = data.split(" ")
    print request

    # Check if first element is GET
    # If not, send HTTP BAD GATEWAY reply
    if(not request[0] == "GET"):
        header = ("""HTTP/1.1 501 Not Implemented\n\n This server can only"""+
        " handle GET requests""")
        connection.send(header)
    else:
        
        # Else take the second element of the request and search for the
        # requested file  
        requested_file = request[1][1:]

        print "requested file: "
        print requested_file
            
        # If requested file not exists send 404
        if(not os.path.exists(requested_file)):

            header = ("""HTTP/1.1 404 Not Found\n\n 404 Error: """+
            """This page cannot be found!""")
            connection.send(header)

        else:   
            
            # Construct reply header
            header = """HTTP/1.1 200 OK\n\n"""

            # Put requested file in variable
            f = open(requested_file, 'r')
            data = f.read()

            connection.send(header + data)


def create_server_socket():
    # Create a socket 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Make address resuable after killing 
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to a port and host
    server_socket.bind((HOST, PORT))

    # Make the server socket listen for a connection
    server_socket.listen(1)
    print "Server is listening..."

    # Keep the server socket alive
    while True:

        # Accept connection 
        connection, address = server_socket.accept()

        # Print the adress that is connected
        print "Connection made between " + str(address) + " and " + str(HOST)
        
        # Handle the client request 
        handle_request(connection)

        print "Request handled. Closing connection"

        # Close the connection
        connection.close()

    # Close the socket
    server_socket.close()

def main():
    create_server_socket()

#http://localhost:8888/index.html


if __name__ == "__main__":
    main()
