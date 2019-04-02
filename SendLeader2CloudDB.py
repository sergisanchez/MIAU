#!/usr/bin/python3
# Send topoDB to cloud. Modulo que envia la topoDB de cada leader a Cloud

#### Imports
import threading, socket,RTM,random
from common import bcolors, custom_print
from time import sleep,time

portCLOUD = 27022
#IP_CLOUD='147.83.159.213'
IP_CLOUD='192.168.4.80'
TopoDB='topoDBfile'
#BROADCASTADDR="147.83.159.223" #Broadcast address
BROADCASTADDR="192.168.4.255" #Broadcast address
BUFSIZE = 65535
def connect2cloud():
    # connect to Cloud
    try:

        Serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Serv_socket.connect((IP_CLOUD, portCLOUD))

    except Exception as ex:
        print('Unable to connect to the Cloud')
        print(ex)

    return Serv_socket

def ReadTopo(Serv_socket):
   myaddr=getmyIP()
   with open(TopoDB) as file:
       for line in file:
           line =eval(line)
           line=line,myaddr
           line=str(line)+':'
           print("sending Line: " + line)
           Serv_socket.send((line).encode())
           data = (Serv_socket.recvfrom(2048))[0].decode('utf-8')
           print("received ack?:",data)
           while data != 'ACK':
               Serv_socket.send((line).encode())
       Serv_socket.send('exit'.encode())
   print("endfile")

def getmyIP():
   # create socket and send
   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
   text = ("")
   sockrcv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   sockrcv.bind(("", 65000))
   # send address
   sock.sendto((str(text)).encode(), (BROADCASTADDR, 65000))

   # receiving data and transmitter address
   data, address = sockrcv.recvfrom(BUFSIZE)
   sockrcv.close()
   sock.close()
   return address[0]

##### MAIN  ###############
def run():

    print("paso1")
    sleep(30)  # delay to give time for updating topoDB
    Serv_socket= connect2cloud()
    ReadTopo(Serv_socket)
    Serv_socket.close()

#run()