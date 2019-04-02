#!/usr/bin/env python3

import pickle, threading

##### VARIABLE DEFINITION  ###############
PORT_IN = 9900
fileReg='regDB'# registration database

######### CLOSE CLOUD ############################

def close_cloud():
    # Cerramos la instancia del socket cliente y servidor

    s.close()


########## START CLOUD  ###########################

def run_cloud():
    global sc, addr, s
    # importamos el modulo socket
    import socket

    # instanciamos un objeto para trabajar con el socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # fog = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Con el metodo bind le indicamos que puerto debe escuchar y de que servidor esperar conexiones
    # Es mejor dejarlo en blanco para recibir conexiones externas si es nuestro caso
    s.bind(("", PORT_IN))

    # Aceptamos conexiones entrantes con el metodo listen, y ademas aplicamos como parametro
    # El numero de conexiones entrantes que vamos a aceptar
    s.listen(1)
    print("Listen Leader by Port:", PORT_IN)


###########  CLOUD RECEIVE FROM LEADER  #####################

def accept_conex_leader():
    while True:
        try:
            # Instanciamos un objeto sc (socket cliente) para recibir datos, al recibir datos este
            # devolvera tambien un objeto que representa una tupla con los datos de conexion: IP y puerto
            (sc, addr) = s.accept()
            t = threading.Thread(target=receive_leader_info, args=(sc, addr), daemon=True)
            t.start()
        except Exception as ex:
            print("error:", ex)


def receive_leader_info(sc,addr):
    # Recibimos el mensaje, con el metodo recvfrom recibimos datos y como parametro
    # la cantidad de bytes para recibir. decode
    try:
        data = sc.recvfrom(2048)[0]
        print("address:", addr)
        data=data.decode()
        print("received data:",data)
        data= eval(data)
        if verific(str(data[0])):
            data = 'True'
            sc.send((data.encode()))
        else:
            sc.send('False'.encode())
            print("USER NOT REGISTERED")
    except Exception as ex:
        print(" void data sent!")



 ######### VERIFICATION USER IN Database webside ########################
def verific(nodeID):
    print('verify ', nodeID,' in dic')
    with open(fileReg,"rb") as f:
        dic=pickle.load(f)
    print(dic)
    if nodeID in dic:
        return True
    else:
        return False
######  MAIN  ########################
def run_checking():
    run_cloud()
    t = threading.Thread(target=accept_conex_leader, args=(), daemon=True)
    t.start()


    #close_cloud()
