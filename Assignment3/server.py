import socket
import os
HOST = 'localhost'
PORT = 8888

# Handles the request of the client
def handle_request(connection):

    # Receive data, 1024 bytes from the buffer.
    data = connection.recv(1024)

    # Split the request on whitespace 
    request = data.split(" ")
    print request

    # Check if first element is GET
    # If not, send HTTP BAD GATEWAY reply
    if(not request[0] == "GET"):
        header = """ HTTP/1.1 501 Not Implemented

This server can only handle GET requests"""
        connection.send(header)
    else:
        
        # Else take the second element of the request and search for the
        # requested file  
        requested_file = request[1][1:]

        print "requested file: "
        print requested_file
            
        # If requested file not exists send 404
        if(not os.path.exists(requested_file)):
            print "Requested file does not exist"
            header ="""HTTP/1.1 404 Not Found
                       

404 Error: This page can not be found!"""
            connection.send(header)
        else:
            
            # Construct OK header
            header ="""HTTP/1.1 200 OK


                    """

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
