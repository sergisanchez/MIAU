#!/usr/bin/env python3
"""""
Checking Agent in Cloud: Leader ckeck ID Agent in cloud
 y obtener un ID
 """

# importamos el modulo para trabajar con sockets
import socket, random

##### VARIABLE DEFINITION  ###############


PORT_IN = 9900
#CLOUD_IP = '147.83.159.213'
CLOUD_IP = '192.168.4.80'


##### START CONNECTION  ###############

def init_connection():
    global s

    # Create socket and listen
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # listening
    # the SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state,
    # without waiting for its natural timeout to expire
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Nos conectamos al servidor con el metodo connect. Tiene dos parametros
    # El primero es la IP del servidor y el segundo el puerto de conexion
    s.connect((CLOUD_IP, PORT_IN))


######### LEADER SEND TO CLOUD #################################
def check2cloud(ID):
    from CP import getmyIP
    # Instanciamos una entrada de datos para que el cliente pueda enviar mensajes

    print("ID :", ID)
    # Con la instancia del objeto servidor (s) y el metodo send, enviamos el mensaje introducido
    s.send(ID.encode())
    found = s.recvfrom(2048)[0]
    found=found.decode()
    print(found)
    return found


######### CLOSE DEVICE ######################
def close_connection():
    # Cerramos la instancia del objeto servidor
    s.close()

    ########### MAIN ########################
"""init_connection()
ID=input("Id: ")
if check2cloud(ID)=="True":
    print("Agent is Registered")
else:
    print("agent Not Registered")
close_connection()
"""
