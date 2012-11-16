#################################################
# Assignment 5a: chat server                    #
# By: Inge Becht, 6093906                       #                         
#                                               #    
#################################################
import socket
import select
import sys

HOST = 'localhost'
PORT = 12345

# Guest count
COUNT = 0 
# List of members
member_list = {} 


# Send the data to all the clients
def say_data(data):
    all_members =  member_list.keys()
    for member in all_members:
        member.sendall(data) 

# A server message.. (same as say data)
def send_server_message(data):
    all_members =  member_list.keys()
    for member in all_members:
        member.sendall("<" + data + ">") 
    
# send data, buy only to receiver and sender
def send_whisper(data, sender, receiver):
    inf = "[" + member_list[sender] + " to " + receiver + "]: "
    data = inf + data
    sender.sendall(data)
    # find key from value possible because names are unique
    all_members =  member_list.keys()
    for member in all_members:
        if member_list[member] == receiver:
            member.sendall(data)

# Checks if a name is in use
def in_use(name):
    if name in member_list.values():
        return True
    return False

# Handles a nickname request from sender
def handle_nick(text, sender):
    if len(text) > 2 or len(text) < 2: 
        sender.sendall("""<Usage of /nick: /nick <enter_name>>""")

    elif(in_use(text[1])) :
        sender.sendall("""<This nickname is already in use>""")

    else:
        temp = member_list[sender]
        member_list[sender] = text[1]
        send_server_message(temp + " changed his name to " + member_list[sender])

# Handle a whisper request from sender
def handle_whisper(text, sender):
    if len(text) < 3:
        sender.sendall("""<Usage of /whisper: /whisper <user> <text>>""")
    elif(not in_use(text[1])):
        sender.sendall("""<This user does not exist>""")
    elif(member_list[sender] == text[1]):
        sender.sendall("""<You can not whisper to yourself>""")
    else:
        send_whisper(" ".join(text[2:]), sender, text[1])

def handle_list(text, sender):
    if len(text) > 1:
        sender.sendall("""<Usage of /list: /list>""")
    else:
        data = "Online visitors:\n"
        all_members = member_list.keys()
        for member in all_members:
            data += member_list[member] + "\n" 
        sender.sendall(data)

        


    
# Run the chat server
def main():
    chat_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Make port resuable after killing 
    chat_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    chat_server.bind((HOST, PORT))
    input = [chat_server]
    # Start listening...
    chat_server.listen(5)
    while True:
        input_ready, _, _ =  select.select(input,[],[])

        for descriptor in input_ready:

            # In case of new client accept 
            if descriptor == chat_server:
                client, _ = chat_server.accept()

                # Add client to all clients and give name
                input.append(client)
                global member_list
                global COUNT
                member_list[client] = "Guest" + str(COUNT)
                COUNT += 1
                send_server_message(member_list[client] + " entered chat")

            # Else handle incoming text of descriptor
            else:
                talk = descriptor.recv(1024)
                
                #TODO: Make sure not too many characters!
                if talk:
                    commands = talk.split(" ")
                    if commands[0] == "/nick":
                        handle_nick(commands, descriptor)

                    elif commands[0] == "/say":
                        say_data( member_list[descriptor] + ": " + 
                                " ".join(commands[1:]))

                    elif commands[0] == "/whisper":
                        handle_whisper(commands, descriptor)
                    
                    elif commands[0] == "/list":
                        handle_list(commands, descriptor)

                    # If none of these commands are used interpret it as a /say
                    else:
                        say_data( member_list[descriptor] + ": " + 
                                " ".join(commands[1:]))

                # In case nothing received we remove 
                # descriptor from input and close the connection
                else:
                    send_server_message(member_list[descriptor] +" logged off")
                    input.remove(descriptor)
                    del member_list[descriptor]
                    descriptor.close()


if __name__ == "__main__":
    main()
