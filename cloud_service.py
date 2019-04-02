#!/usr/bin/python3
# Cloud Service
"""""
activamos la atencion del service en cloud. Se obtiene la topoDB
 de cada leader y se construye una cloudDB.
 Espera peticiones de los leaders sobre recurso necesarios y proporciona
 la IP del leader que tiene el recurso
 """

#### Imports
import threading, socket
import pickle
#from common import bcolors, custom_print
#from time import sleep,time


portUPDTD = 27022 # localhost port to attend updating
portSERV= 27020# localhost port to service attend
_connected = True
CloudDB='CloudDBfile'
DB2work = {}


def CreateF2Cconnect():
    global updtd_socket
    try:
        # Create socket and listen
        updtd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # listening
        # the SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state,
        # without waiting for its natural timeout to expire
        updtd_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Specify the welcoming port to receive
        updtd_socket.bind(('', portUPDTD))
        print('OK Updating Attention created.')
    except Exception as ex:
        print('Unable to create updating socket')
        print(ex)


def LeaderAtt():

    updtd_socket.listen(1)

    while _connected:

        try:
            (dat, address) = updtd_socket.accept()
            # Create new thread for each new connection
            t = threading.Thread(target=RecvTopoLeader,args=(dat,address),daemon=True)
            t.start()

        except Exception as ex:
            print(ex)
            return


def RecvTopoLeader(dat,address):

    data=''
    while data !='exit':
        try:
            data = (dat.recvfrom(2048))[0].decode('utf-8')

            print("Data recv:", str(data))
            if data != '':
                print("data Ok")
                dat.send('ACK'.encode('utf-8'))
            eledata = data.split(':')
            for elem in eledata:

                # creamos un locl al thread para garantizar sincronizacion
               with threading.Lock():
                    updateCloudDB(elem)



        except Exception as ex:

            print(" NO data received!")
            return


### format od data: (('SEM', 'MA', "(742, '1234')", '192.168.4.117', 'lig'), '192.168.4.62')
def updateCloudDB(data):
    try:
        data = eval(data)
        index = eval(data[0][2])
        print('update Cloud DB with data: ', index[0], ' in DB2work')

        with open(CloudDB, "rb") as f:
            DB2work = pickle.load(f)

        DB2work[index[0]] = (data[0], data[1])
        print("updated:",DB2work)
        save_dic(DB2work)

    except Exception as ex:
        print(" void data received!")


def initTopoCloud():
     save_dic(DB2work)

def save_dic(dic):

    with open(CloudDB,"wb") as f:
        pickle.dump(dic,f)


def CreateServConnect():
    global serv_socket
    try:
        # Create socket and listen
        serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # listening
        # the SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state,
        # without waiting for its natural timeout to expire
        serv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Specify the welcoming port to receive
        serv_socket.bind(('', portSERV))
        print('OK Service Attention created.')
    except Exception as ex:
        print('Unable to create service socket')
        print(ex)

def ServAtt():
    serv_socket.listen(1)

    while _connected:

        try:
            (dat, address) = serv_socket.accept()
            # Create new thread for each new connection
            t = threading.Thread(target=RecvServMsg, args=(dat, address))
            t.start()

        except Exception as ex:
            print(ex)
            return

def RecvServMsg(dat,address):
    try:

        data = (dat.recvfrom(2048))[0].decode('utf-8')
        #print('recv msg \'' + data + '\'')
        # rec_raw = (sc.recvfrom(2048))[0].decode('utf-8')
        # data = data.decode('utf-8')
        # data = eval(data)
        print('received message: ',data, 'from @IP: ', address[0])
        ##### Analize  Received Opcions ###################
        data = data.split(':')
        if data[0] == 'SEARCH':
            iotlist = eval(data[1])
            print(iotlist, type(iotlist))
            print('Checking CloudDB..........')
            IoTfound, leaderAddr = CheckCloudDB(iotlist)
            print('IoT Found, LeaderAddr: ', IoTfound, leaderAddr)
            if IoTfound:
                mesg = "SEARCH:" + str(data[1])
                # send to cloud Addr=@Cloud
                UpAddr = leaderAddr
                rol = "Leader"
                t = threading.Thread(target=Send_Serv, args=(rol, mesg, UpAddr), daemon=True)
                t.start()
    except Exception as ex:
        print(ex)
        return

def CheckCloudDB(data):
    found = False
  """""  with open(CloudDB, 'r') as file:
        for linea in file:
            print(linea)
            linea = eval(linea)

            print('linea[0]:', linea[0])
            tup = tuple(linea[0])
            #print('tup[4]', tup[4])

            if data in tup[4]:
                found = True
                break
    #print('iot:', tup[4], 'IP leader:', linea[1])
    return found, linea[1]"""

    try:
        data = eval(data)
        index = eval(data[0][2])
        iot= eval(data[0][4])
        # load dictionary from database
        with open(CloudDB, "rb") as f:
            DB2work = pickle.load(f)

        #reading dictionary and find iot

        for index,content in DB2work:
            content=eval(content)
            if iot == content[0][4]:
                found=True
                break
    return found,content[1]


    except Exception as ex:
        print(" void data received!")

def Send_Serv(rol,mesg, AgentAddr):
    try:
        # connect to leader and send mesg
        Serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Serv_socket.connect((AgentAddr, portSERV))
        print("sending mesg: "+str(mesg)," to the " +str(rol))
        Serv_socket.send((mesg).encode())
        Serv_socket.close()
    except Exception as ex:
        print('Unable to connect to the Leader')
        print(ex)

############ MAIN  ###########################
def cloud_service_run():

    initTopoCloud()
    CreateF2Cconnect()
    CreateServConnect()

    th = threading.Thread(target=LeaderAtt, args=(),daemon= True)
    th.start()
    tx = threading.Thread(target=ServAtt, args=(),daemon= True)
    tx.start()




