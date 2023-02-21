import subprocess
import threading
import datetime
import os
import time

# command line command to start server is "socat TCP-LISTEN:PORT_NUMBER,fork EXEC:/bin/bash"
# from there you just need to change the server_ip variable to the ip of your server, server_port to whatever port number you put in the command,
# and chatLog_filename to whatever the name/location is of where the chat file is being stored.

server_ip = "10.1.1.1"
server_port = "12345"
chatLog_filename = "chat.log"


def refreshChat(flag, client):
    while not flag.is_set():
        _ = os.system('clear')
        client.stdin.write(b'cat ' + chatLog_filename.encode('utf-8') + b'\n')
        client.stdin.flush()
        response = client.stdout.readline()
        print(response.decode('utf-8'))
        time.sleep(10)


def sendMessage(flag, client, refreshThread):
    connect = True
    while connect:
        msg = input("Please enter your message, or type exit to quit: ")
        if msg == "exit":
            connect = False
        else:
            client.stdin.write(b'echo "' + msg.encode('utf-8') + b'" >> ' + chatLog_filename.encode('utf-8') + b'\n')
            client.stdin.flush()
            flag.set()
            refreshThread.join()
            flag.clear()
            refreshThread = threading.Thread(target=refreshChat, args=(flag, client,))
            refreshThread.start()


def chat(name):
    with subprocess.Popen(['nc', server_ip, server_port], stdin=subprocess.PIPE, stdout=subprocess.PIPE) as client:
        cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        client.stdin.write(b'echo "' + cur_time.encode('utf-8') + b': ' + name.encode(
            'utf-8') + b' is entering the chat." >> ' + chatLog_filename.encode('utf-8') + b'\n')
        client.stdin.flush()

        flag = threading.Event()
        t1 = threading.Thread(target=refreshChat, args=(flag, client,))
        t2 = threading.Thread(target=sendMessage, args=(flag, client, t1))
        t1.start()
        t2.start()

        t2.join()
        flag.set()
        cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        client.stdin.write(b'echo "' + cur_time.encode('utf-8') + b': ' + name.encode(
            'utf-8') + b' has left the chat." >> ' + chatLog_filename.encode('utf-8') + b'\n')
        client.stdin.flush()


if __name__ == '__main__':
    print(
        "Welcome to Netcat Chat!\nOnce you have entered a username, you will join the chat. Chat refreshes every 10 seconds, or whenever you send a message, so make sure you type your message before that! :)")
    username = input("Please enter a username: ")
    chat(username)
