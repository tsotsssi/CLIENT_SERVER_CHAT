# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 18:39:53 2020

@author: REY
"""


import threading
import socket
import os

SEPARATOR = '<SEPARATOR>'
UPLOAD = '<UPLOAD>'
DOWNLOAD = '<DOWNLOAD>'

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host = '172.0.0.1'
port=55555

client.connect((host,port))


# First we verify the identity of the client
login = False
while login == False:
    username = input('Enter your username >')
    password = input('Enter your password >')
    client.send(f'{username}{SEPARATOR}{password}'.encode('ascii'))
    server_reponse = client.recv(1024).decode('ascii')
    if server_reponse == 'TRUE':
        login = True
    elif server_reponse == 'FALSE':
        print('Username or Password incorrect !')
    
    

def receive(): # Handle the message received
    while True:
        try:
            try:                
                message = client.recv(1024).decode('ascii')
                if message == 'USER':
                    client.send(username.encode('ascii'))
                elif(len(message.split(DOWNLOAD))==2):
                    filename = message.split(DOWNLOAD)[1]
                    file = open(filename,'wb')  
                    data = client.recv(65536)
                    file.write(data)
                    file.close()
                    print(f'File {filename} successfully downloaded from the server !')
                else:
                    print(message)
            except:
                pass
        except:
            print('An error occured !')
            client.close()
            break

def write_msg(): # Handles the input of the client
    while True:
        client_input = f'{input("")}'
        if(client_input.startswith('#upload')): #upload filename
            upload(client_input.split(' ')[1])
        elif(client_input.startswith('#download')): #download filename
            download(client_input.split(' ')[1])
        else:
            if(len(client_input)<280):
                message = f'{username}: {client_input}'
                client.send(message.encode('ascii'))
            else:
                print('Message too long ! It must be below 280 characters.')
            
def upload(filename): # Transfers the selected file to the server
    try:
        filesize = os.path.getsize(filename)
        if(filesize < 65536):        
            client.send(f'{UPLOAD}{SEPARATOR}{filename}{SEPARATOR}{filesize}{SEPARATOR}{username}'.encode('ascii'))
            # start sending the file       
            file = open(filename, "rb")
            data = file.read(65536)
            client.send(data)
            file.close()
            print("File sent !")
        else:
            print('The file is too heavy for the server (max 65ko)')
    except:
        print('File not found.')
    
def download(filename): # Asks and receives the asked file from the server
    client.send(f'{DOWNLOAD}{SEPARATOR}{filename}{SEPARATOR}{username}'.encode('ascii'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write_msg)
write_thread.start()