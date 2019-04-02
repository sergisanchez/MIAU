import threading
import socket
import json
from FrontendInterface import AgentLog, AgentOPerationCodes
from time import sleep,time
from random import randint

IPFrontEnd = '147.83.159.206'
PortFrontEnd = 3884

def connect2Fend():
    # connect to Cloud
    try:

        Serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Serv_socket.connect((IPFrontEnd, PortFrontEnd))

    except Exception as ex:
        print('Unable to connect to the Fend')
        print(ex)

    return Serv_socket

def sedingData(Serv_socket):
    send_info ={
        'id_source': '123',
        'id_destination': '456',
        'op_code': '120',
        'timestamp': '121846312',
    }
    """i=0
    while i < 20:
        send_info['id_source']=str(int(send_info['id_source'])+1)
        send_info['id_destination'] = str(int(send_info['id_destination']) + 1)
        send_info['op_code'] = str(int(send_info['op_code']) + 1)
        send_info['timestamp'] = str(int(send_info['timestamp']) + 1)

        #print(send_info)
        i=i+1
        line=json.dumps(send_info)
        print(json.loads(line))"""

    al = AgentLog(str(randint(123,125)), '456', '12op', additionalData='SomeDataHere')
    j = al.getJSON()
    print(j)
    print('al', al)
    ## Lo que el programa mF2C envia: string j (JSON)
    print('sending json...')
    Serv_socket.send(j.encode('utf-8'))
    Serv_socket.recv(1024)
    print('sending OK.next data..')
###### MAIN  #############
serv_socket=connect2Fend()
while True:
    sleep(3)
    sedingData(serv_socket)
