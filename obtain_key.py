#!/usr/bin/env python3
"""""
identiifcation: el agent antes de entrar a f2c se debe identifia
 y obtener un ID
 """

#importamos el modulo para trabajar con sockets
import socket, random
##### VARIABLE DEFINITION  ###############


PORT_IN = 9999
##CLOUD_IP='147.83.159.213'
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
    #Nos conectamos al servidor con el metodo connect. Tiene dos parametros
    #El primero es la IP del servidor y el segundo el puerto de conexion
    s.connect((CLOUD_IP, PORT_IN))

######### AGENT SEND TO CLOUD #################################
def send2cloud(type):
    from RTM import getmyIP
    #Instanciamos una entrada de datos para que el cliente pueda enviar mensajes
    email =type+"@"+getmyIP()
    agnt_type=type
    id_key= '1234'
    ID = compute_ID(int(id_key))
    print("ID :",str(ID))
    #Con la instancia del objeto servidor (s) y el metodo send, enviamos el mensaje introducido
    s.send((email+' '+agnt_type+' '+id_key+' '+str(ID)).encode())
    print(email+' '+agnt_type+' '+id_key+' '+str(ID))
 
    return id_key,ID

######### COMPUTE ID ########################

def compute_ID(id_key):

    # compute ID
    return random.randint(0,id_key)


######### CLOSE DEVICE ######################
def close_connection():

    #Cerramos la instancia del objeto servidor
    s.close()

########### MAIN ########################
#if __name__ == "__main__":
#run_dev()
# send2cloud('car')
#close_dev()
