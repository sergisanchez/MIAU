#!/usr/bin/env python3
import threading
import pickle
import cloud_check_id as check
import random
from time import sleep
##### VARIABLE DEFINITION  ###############

dic={} #registration dictionary
fileReg='regDB'# registration database
PORT_IN = 9999

def save_dic(dic):

    with open(fileReg,"wb") as f:
        pickle.dump(dic,f)

def load_dic():
    with open(fileReg,"rb") as f:
        return pickle.load(f)



########## setup regDB to store registration DB ###################

def update_regDB():
    pass

######### VERIFICATION USER IN MsQl Database webside ########################
def verific():
    return True

######### REGISTRATION PROCESSING###############

def processing(data):
    data = data.decode().split(' ')
    dic=load_dic()
    #print("dic antes:", dic)
    dic[data[3]]=(data[0],data[1],data[2])
    #obtain parameters form receiver_fog function
    print("dic despues:",dic)
    save_dic(dic)


######### CLOSE CLOUD ############################

def close_cloud():

    #Cerramos la instancia del socket cliente y servidor
    s.close()

########## START CLOUD  ###########################

def run_cloud():
    global sc,addr,s
    #importamos el modulo socket
    import socket
 
    #instanciamos un objeto para trabajar con el socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #fog = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Con el metodo bind le indicamos que puerto debe escuchar y de que servidor esperar conexiones
    #Es mejor dejarlo en blanco para recibir conexiones externas si es nuestro caso
    s.bind(("", PORT_IN))
 
    #Aceptamos conexiones entrantes con el metodo listen, y ademas aplicamos como parametro
    #El numero de conexiones entrantes que vamos a aceptar
    s.listen(1)
    print("Listen Agents by Port:",PORT_IN)
 


###########  CLOUD RECIVE FROM FOG  #####################

def accept_conex_agent():
    global data
    while True:
        try:
            # Instanciamos un objeto sc (socket cliente) para recibir datos, al recibir datos este
            # devolvera tambien un objeto que representa una tupla con los datos de conexion: IP y puerto
            (sc, addr) = s.accept()
            t = threading.Thread(target=receive_agent_info, args=(sc,addr), daemon=True)
            t.start()
        except Exception as ex:
            print("error:", ex)

def receive_agent_info(sc,addr):
    #Recibimos el mensaje, con el metodo recvfrom recibimos datos y como parametro
    #la cantidad de bytes para recibir. decode
    data= sc.recvfrom(2048)[0]
    #print("address:",addr)
    #print("received data:", data.decode())
    if verific():
        processing(data)
    else:
        print("USER",addr," NOT REGISTERED")

def initfileReg():

    open(fileReg, 'wb')
    save_dic(dic)

######  MAIN  ########################
def cloud_reg_run():
    initfileReg()
    run_cloud()
    th1 = threading.Thread(target=accept_conex_agent, args=(), daemon=True)
    th1.start()

    th2 = threading.Thread(target=check.run_checking, args=(), daemon=True)
    th2.start()

    while input("-->") != "exit":
        pass

    #update_regDB()
    close_cloud()
    check.close_cloud()
