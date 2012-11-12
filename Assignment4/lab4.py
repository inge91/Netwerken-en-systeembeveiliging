#################################################
# Assignment 4: SMTP client python              #
# By: Inge Becht, 6093906                       #                         
#                                               #    
# Run program by: python lab4.py                #            
#                                               #
#################################################
## Answer for the question:
## To send mail with authentication, one could for example use SMTP AUTH or POP3 instead
## of simply SMTP. In case of this SMTP AUTH the user has to verify its identity
## by providing a username and password connected to the server when sending the
## email. The server is able to check if these credentials are then legit and
## the email will be sent. POP 3 works the same way with asking for credentials
## after establishing a conversation.
import socket
import sys

HOST = "smtp.uva.nl"
PORT = 25

# dict with error codes (thanks
# to http://www.greenend.org.uk/rjk/tech/smtpreplies.html)
error_codes = {"211":"System status, or system help reply",
"214":"Help message",
"251":"User not local; will forward to <forward-path>",
"354":"Start mail input; end with <CRLF>.<CRLF>",
"421": HOST + " Service not available, closing transmission channel",
"450":"Requested mail action not taken: mailbox unavailable",
"451":"Requested action aborted: local error in processing",
"452":"Requested action not taken: insufficient system storage",
"500":"Syntax error, command unrecognised",
"501":"Syntax error in parameters or arguments",
"502":"Command not implemented",
"503":"Bad sequence of commands",
"504":"Command parameter not implemented",
"521": HOST + " does not accept mail (see rfc1846)",
"530":"Access denied (???a Sendmailism)",
"550":"Requested action not taken: mailbox unavailable",
"552":"Requested mail action aborted: exceeded storage allocation",
"553":"Requested action not taken: mailbox name not allowed",
"554":"Transaction failed"}


# Receives all data so nothing stays in buffer
#def flush_socket(client_socket):
#    while True:
#        server_response = client_socket.recv(1024)
#        if "\n" in server_response:
#            break

# Initiate conversation with smtp server
def initiate_conversation(client_socket):
    client_socket.sendall("HELO " + 'localhost' + "\r\n")
    server_response = client_socket.recv(1024)
    code = server_response.split(" ")[0]
    
    # Error handling
    if code == "220":
        print "Established connection with server"
        return True
    else:
        error_message = error_codes.get(code, ("Error " + code + 
                          ": Unknown response code"))
        print "Error " + code + ": " + error_message + "\nClosing connection\n"
        return False

# Establish email address from sender to server
def establish_sender(client_socket):
    # Prompt user for their email addres and send it to the server
    sender = raw_input("What is your email address?\n>")

    client_socket.sendall("MAIL FROM: "+ sender  +"\r\n")
    server_response = client_socket.recv(1024)
    code = server_response.split(" ")[0]
    
    # Error handling
    if code == "250":
        print "Established sender" 
        return True
    else:
        error_message = error_codes.get(code, ("Error " + code + 
                          ": Unknown response code"))
        print "Error " + code + ": " + error_message + "\nClosing connection\n"
        return False
        
# Establish the recipient email address to the server
def establish_recipient(client_socket):
    # Prompt user for recipient
    recipient = raw_input("What is the recipients email address?\n>")

    client_socket.sendall("RCPT TO: "+ recipient +"\r\n")
    server_response = client_socket.recv(1024)
    code = server_response.split(" ")[0]

    # Error handling
    if code == "250":
        print "Established recipient" 
        return True
    else:
        error_message = error_codes.get(code, ("Error " + code + 
                          ": Unknown response code"))
        print "Error " + code + ": " + error_message + "\nClosing connection\n"
        return False

# Establish the to be send data to the server
def establish_data(client_socket):
    client_socket.sendall("DATA\r\n")
    server_response = client_socket.recv(1024)
    server_response = client_socket.recv(1024)

	# prompt user for data and send to server
    print "Type in your message body. Enter a single \".\" when done.\n>"
    data = "" 
    while(True):
        next_input = raw_input("")
        if(next_input == "."):
            break
        else:
            data += "\n"
            data += next_input

    client_socket.sendall(data + "\n.\r\n")
    server_response = client_socket.recv(1024)
    code = server_response.split(" ")[0]
    
    # Error handling
    if code == "250":
        print "Message accepted for delivery" 
        return True
    else:
        error_message = error_codes.get(code, ("Error " + code + 
                          ": Unknown response code"))
        print "Error " + code + ": " + error_message + "\nClosing connection\n"
        return False
	

# Creates client that can connect to smtp.uva.nl
def handle_email(client_socket):
    success = initiate_conversation(client_socket)
    # If conversation can not be initiated the whole script won't work
    # so exit
    if success == False:
        print "Exiting..."
        sys.exit(1)

	handled = False
	# Handle all elements of sending an email 
   
    if establish_sender(client_socket) == False:
        print "Exiting..."
        sys.exit(1)

    if establish_recipient(client_socket) == False:
        print "Exiting..."
        sys.exit(1)
	
    if establish_data(client_socket) == False:
        print "Exiting..."
        sys.exit(1)

    # Quit the sdtp connection
    client_socket.sendall("QUIT\r\n")
    server_response = client_socket.recv(1024)
    #print server_response
    code = server_response.split(" ")[0]
    if(code == "221"):
        pass
    else:
        print "Could not QUIT.. Exiting..."
        sys.exit(1)

def main():
    #prompt the user to input
    while(True):
         # Construct the client socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Let the socket connect to host smtp.uva.nl at port 25
        client_socket.connect((HOST, PORT))

        reply = raw_input("Want to send an email?[y/n]")
        if(reply == "y"):
            handle_email(client_socket)
            client_socket.close()
        else:
            client_socket.close()
            break

    print "Exiting..."




if __name__ == "__main__":
    main()

