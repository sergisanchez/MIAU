import threading
import socket
from time import sleep,time

IPsem = '10.6.27.6'  ## semafor
#IPsem = '10.15.66.217'  ## old car
#IPsem = '10.4.148.101'  ## new car
Portsem = 6510

def connect2sem():
    # connect to Cloud
    try:

        Serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Serv_socket.connect((IPsem, Portsem))

    except Exception as ex:
        print('Unable to connect to the sem')
        print(ex)

    return Serv_socket

def sedingData(Serv_socket):

    print('sending data...')
    Serv_socket.send('GREEN'.encode('utf-8'))
    Serv_socket.recv(1024)
    print('sending OK.next data..')
###### MAIN  #############
serv_socket=connect2sem()
sedingData(serv_socket)
