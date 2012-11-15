import socket
import gui
import time
import select
from threading import Thread
HOST = 'localhost'
PORT = 12345

class Listen(Thread):
    def __init__(self, chat_client, w):
        Thread.__init__(self)
        self.daemon = True
        self.chat_socket= chat_client
        self.window = w

    def run(self):
        while True:
            data = self.chat_socket.recv(1024)
            self.window.writeln(data)
        

class Send(Thread):
    def __init__(self, chat_client, w):
        Thread.__init__(self)
        self.daemon = True
        self.chat_socket= chat_client
        self.window = w

    def run(self):
        line = self.window.getline()
        if line:
            self.chat_socket.sendall(line)


def main():
    chat_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    chat_client.connect((HOST, PORT))
    chat_client.setblocking(0)

    w = gui.MainWindow()

    listen = Listen(chat_client, w)
    send = Send(chat_client, w)

    listen.start()
    send.start()

    while w.update():
       pass
    
    listen.join()
    send.join()

if __name__ == "__main__":
    main()
