# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 18:22:55 2020

@author: REY
"""

from datetime import datetime
import sqlite3
import threading
import socket

SEPARATOR = '<SEPARATOR>'
UPLOAD = '<UPLOAD>'
DOWNLOAD = '<DOWNLOAD>'

host = '172.0.0.1'
port=55555

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((host, port))
server.listen(50)

clients = []
usernames = []
# store the names of the available files when a new file is uploaded
available_files = [] 

def broadcast(message):
    for client in clients:
        client.send(message)
        
def handle(client): # Handle the interactions with the client
    while True:
        try:
            message = client.recv(1024)
            if(message.decode('ascii').split(SEPARATOR)[0]==UPLOAD):
                receive_file(client, message.decode('ascii').split(UPLOAD)[1])
            elif(message.decode('ascii').split(SEPARATOR)[0]==DOWNLOAD):
                send_file(client, message.decode('ascii').split(DOWNLOAD)[1])
            else:
                broadcast(message)
        except:
            if(client in clients):
                index = clients.index(client)
                clients.remove(client)
                client.close()
                username = usernames[index]
                broadcast(f'{username} left the chat'.encode('ascii'))
                usernames.remove(username)
            break
        
def receive_file(client, info_file): # This method allows the server to receive a file
    filename = info_file.split(SEPARATOR)[1]
    sender = info_file.split(SEPARATOR)[3]
    file = open(filename,'wb')
    data = client.recv(65536)
    file.write(data)
    file.close()
    available_files.append(filename)
    print(f'File received {filename} (sent by {sender})')
    broadcast(f'New file {filename} sent by {sender} is now available from the server'.encode('ascii'))

def send_file(client, info_file):
    filename = info_file.split(SEPARATOR)[1]
    receiver = info_file.split(SEPARATOR)[2]
    if(filename in available_files):        
        file = open(filename,'rb')
        data = file.read(65536)
        client.send(f'{DOWNLOAD}{filename}'.encode('ascii'))
        client.send(data)
        file.close()
        print(f'File {filename} successfully sent to {receiver}')
    else:
        client.send('Asked file not available on the server :('.encode('ascii'))
        
def kill():
    while True:
        command_line = f'{input("")}'
        command = command_line.split(" ")[0]
        if(command=='#kill'):
            client_name = command_line.split(" ")[1]
            if(client_name in usernames):
                name_index = usernames.index(client_name)
                client_to_kill = clients[name_index]
                clients.remove(client_to_kill)
                client_to_kill.send('You have been disconnected from the server.'.encode('ascii'))
                client_to_kill.close()
                usernames.remove(client_name)
                broadcast(f'{client_name} has been disconnected from the server'.encode('ascii'))
                print(f'{client_name} has been successfully disconnected from the server')
            else:
                print(f'{client_name} do not exist among the clients.')
        else:
            print('Invalid command line !')
            print(f'{command} is not a valid command.')

def receive():
    # We limit the number of client to 50 simultaneously
    while len(clients) < 50:
        client, address = server.accept()
        
        # We check if the client is registered in the database
        login = False
        con = sqlite3.connect('chat_user_storage.db') #Connection with the database
        cur = con.cursor()
        while login == False:
            id_client = client.recv(1024).decode('ascii')
            username = id_client.split(SEPARATOR)[0]
            password = id_client.split(SEPARATOR)[1]
            cur.execute("select * from logins where name=:username and password=:password", {"username": username, "password": password})
            tmp = (cur.fetchone())
            if tmp == None : 
                client.send('FALSE'.encode('ascii')) # If the id are not correct send FALSE
            else :
                client.send('TRUE'.encode('ascii')) # if the id ar correct send TRUE
                login = True
        con.commit()
        con.close()
        
        date = datetime.now()
        print(f'New client connected with {str(address)} at {date}')
        
        client.send('USER'.encode('ascii'))

        username = client.recv(1024).decode('ascii').split(':')[0]

        usernames.append(username)
        clients.append(client)
        
        print(f'Username of the client is {username}')
        broadcast(f'{username} joined the chat'.encode('ascii'))
        client.send('Connected to the server !'.encode('ascii'))
        
        thread_handle = threading.Thread(target=handle, args=(client,))
        thread_handle.start()
        
        thread_kill = threading.Thread(target=kill)
        thread_kill.start()

print("Server is listening...")
receive()