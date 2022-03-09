#!/usr/bin/python3
# CP module

#### Imports
import threading, socket,random
from common import bcolors, custom_print
from time import sleep,time
import requests
import json
import os
import subprocess
import pymysql

#### TODO: Review Private variables
__setup_done__ = False
cp = None
_tag = bcolors.HEADER+'CP'+bcolors.ENDC
_ip_cbk = None
_role_cbk = None

#### Global variables

BROADCASTADDR="147.83.159.223" #Broadcast address
#BROADCASTADDR="192.168.4.255" #Broadcast address
BUFSIZE = 65535
port2IP=27016 #localhost port to send LEADER ip to DataPlane
port2DB=27015# localhost port to send topology database to DataPlane
ipLEADER2=0 # initialazing to localhost to test
flag='LEADER2'
portTCP='27000'
oncetime=1# Open only once TCP connection in LEADER1
checkAddr='0.0.0'
count=0
LEADERsock='None'
AGENTsockExist=False
#IoT components ######
IoT_SEM = ('sem')
IoT_AMB =('amb')
IoT_BOM = ('bom')
IoT_CAR = ('cam','sens')
IoT_BUI_F = ('temp')
IoT_BUI_I = ('incl')
IoT_BUI_J = ('jam')
#########################

_connected = False
_AGENTconnected=False
_role = None
_type = None
_BcastIP = None
_nodeID = None
IoT = None
portUDP = '10600'
thread_module = None
upt_lock=threading.Lock()
############################################################################
#
#                       CLASSES
#
############################################################################
class socketTCP:
    NodeSock = None

    def __init__(self, inode):
        self.node_info = inode

    def CreateAGENTSock(self):
        self.NodeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # listening
        #the SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state,
        # without waiting for its natural timeout to expire
        self.NodeSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.NodeSock.connect((node_info['leaderIP'],int(node_info['portTCP'])))
        return self.NodeSock

    def CreateLEADERSock(self):
        # Create socket and listen
        self.NodeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # listening
        # the SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state,
        # without waiting for its natural timeout to expire
        self.NodeSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Specify the welcoming port to receive
        self.node_info['portTCP']=int(self.node_info['portTCP'])
        self.NodeSock.bind(('', self.node_info['portTCP']))
        print('OK Connection created.')
        self.NodeSock.listen(1)


    def attendSock(self):
        print("waiting InfoNode...")
        (sc, addr) = self.NodeSock.accept()
        return sc, addr

    def ReadSock(self,connectSock):
        try:
            data = connectSock.recvfrom(2048)[0].decode('utf-8')

        except Exception as ex:
            cp.eprint(ex,"Connection closed")
            data = " "
            pass

        return data

    def WriteSock(self, ConnectSocket,node_info):
        print('Thread:', threading.current_thread().getName(), 'with identifier:', threading.current_thread().ident)
        ConnectSocket.sendto(str(node_info).encode(),(node_info['myIP'],int(node_info['portTCP'])))

    def CloseSock(self):
        print("Close Connection")
        self.NodeSock.close()

# class ldb : mysql DDBB to regidter node info
class ldb:
    cursor=None
    db=None

    """def __init__(self, inode):
       self.node_info = inode"""
    def conect(self):
        user=os.environ["USER"]
        self.db = pymysql.connect("localhost",user,"miau","LOCALDB" )

        # prepare a cursor object using cursor() method
        self.cursor = self.db.cursor()
    def reset(self):
        # Drop table if it already exist using execute() method.
        self.cursor.execute("DROP TABLE IF EXISTS info")

        # Create table as per requirement
        sql = """CREATE TABLE info (
         features  VARCHAR(500))"""
        try:
            # Execute the SQL command
            self.cursor.execute(sql)
            # Commit your changes in the database
            self.db.commit()
        except:
            # Rollback in case there is any error
            print("Error to create table in local DB")
            self.db.rollback()

    def update(self,node_info):

        sql = "INSERT INTO `info`(features) VALUES (%s)"

        try:
            # Execute the SQL command
            self.cursor.execute(sql,json.dumps(node_info))
            # Commit your changes in the database
            self.db.commit()
        except:
            # Rollback in case there is any error
            self.db.rollback()

    def get(self):
        # read tables
        self.cursor.execute(" select * from info")
        for fila in self.cursor:
            fila=json.loads(fila[0])
        return fila

    def close(self):
        # disconnect from server
        self.db.close()


###############################################
#                   Threads
###############################################

def th_module():
    global _connected, node_info, socketTCP, LEADERsock, _AGENTconnected, localDB


    # select AGENT/LEADER

    if node_info['role'] == 'LEADER':
        print("running as a LEADER \n")
        node_info['leaderIP']=node_info['myIP']

        LEADERsock=socketTCP(node_info)

        #CreateSocketTCP()
        LEADERsock.CreateLEADERSock()
        run = threading.Thread(name="Transmitt running as a LEADER", target=transmitterUDP, args=(node_info,), daemon=True)
        run.start()
        run.join()

        run = threading.Thread(name="receiv running as a LEADER", target=attentRequestTCP,daemon=True)
        run.start()
        # Create instance to class local DB and connect
        localDB = ldb()
        localDB.conect()
        localDB.reset()
        print("LocalDB connected")
        # Register info LEADER in loclaDB
        localDB.update(node_info)

        #### refresh IP LEADER

        fresh = threading.Thread(name="refresh", target=refresh,daemon=True)
        fresh.start()
    else:
        print("running as a AGENT \n")
        localDB = ldb()
        localDB.conect()
        localDB.reset()
        print("LocalDB connected")
        _AGENTconnected=True
        run = threading.Thread(name="receiv BroadCast as AGENT", target=receiverUDP,
                               daemon=True)
        run.start()


    #3. Wait loop
    while _connected:
        pass
    localDB.close()


###############################################
#                   Functions
###############################################
def get_bcastaddr():
    bcastlist = []
    index = 0
    info = subprocess.check_output(['ip', 'addr']).decode()
    info = info.split('\n')
    for line in info:
        if 'inet' in line:
            if 'brd' in line:
                line = line.split(' ')
                bcastlist.append(line[7])
    for addr in bcastlist:
        print(index, ".- ", bcastlist[index])
        index = index + 1
    bcastaddr=None
    while bcastaddr==None:
        selec = input("Select BcastAdrr:")
        selec = int(selec)
        if selec < index:
            print("Bcast selected:", bcastlist[selec])
            bcastaddr=bcastlist[selec]
        else:
            print("no selection")
            bcastaddr=None
    return bcastaddr

def getmyIP (node_info):
    myIP = "0.0.0.0"
    setAdrress = subprocess.check_output(["hostname", "-I"]).decode()
    list = setAdrress.split(" ")
    for elem in list:
        if node_info['BcastIP'].split(".")[0] == elem.split(".")[0]:
            myIP = elem
    print("my IP ADDR:",myIP)
    return myIP

def transmitterUDP(node_info):

    global start_setuptime,sock, LEADERsock
    print('Thread:', threading.current_thread().getName(), 'with identifier:', threading.current_thread().ident)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
 ## start setup time counter
    start_setuptime=time()
 # send device and role
    node_info['portUDP']=int(node_info['portUDP'])
    sock.sendto((str(node_info)).encode(), (node_info['BcastIP'], node_info['portUDP']))
    sock.close()

def AGENTattended(connecAGENTsock):

    global _AGENTconnected, AGENTsock, node_info,AGENTsockExist, LEADERsock
    print('Thread:', threading.current_thread().getName(), 'with identifier:', threading.current_thread().ident)

    try:

        while _AGENTconnected:
            data=AGENTsock.ReadSock(connecAGENTsock)
            #print("Data:", data)
            if data != " ":
                data=eval(data)
                ProccesData(connecAGENTsock, data)
    except Exception as ex:
        if node_info['role']=='BKUPGENT':

            print('Unable to connect to the LEADER')
            print('Agent Backup change role to Leader')
            # close receiver TCP socket as AGENT
            AGENTsock.CloseSock()
            print('Socket TCP to LEADER closed')
            # close receiver UDP socket as AGENT
            _AGENTconnected=False
            print('Socket UDP AGENT closed')
            AGENTsockExist = False
            # Checking API up
            try:
                API_addr_get = 'http://' + node_info['myIP'] + ':8000/get_topoDB'
                requests.get(API_addr_get)
                print("API is Running")
            except Exception as ex:
                print("*********** Start API ******")
                os.system("hug -f API_node.py & ")
                # Reset globalDB by the LEADER
                sleep(5)
            # remove failed leader to globlaDB
            PARAMS = "index={'myIP':" + "'" + node_info['leaderIP'] + "'}"
            API_addr_del = 'http://' + node_info['myIP'] + ':8000/del_topoDB'
            response = (requests.get(API_addr_del, PARAMS)).json()
            # update info new leader
            node_info['role'] = 'LEADER'
            node_info['leaderIP'] = node_info['myIP']
            print("I'm new leader:", node_info)
            updattingDB(node_info)

            # comunicateRole('LEADER')
            # Create instance to class socketTCP
            LEADERsock = socketTCP(node_info)

            # CreateSocketTCP()
            LEADERsock.CreateLEADERSock()
            run = threading.Thread(name="Transmitt running as a newLEADER", target=transmitterUDP, args=(node_info,),
                                   daemon=True)
            run.start()
            run.join()
            print("Receive as new LEADER")
            run = threading.Thread(name="receiv running as a new LEADER", target=attentRequestTCP,
                                   daemon=True)
            run.start()
            #### refresh IP LEADER

            fresh = threading.Thread(name="refresh", target=refresh,
                                     daemon=True)
            fresh.start()
            exit(0)
        elif node_info['role']=='AGENT':
            AGENTsock.CloseSock()
            AGENTsockExist = False
            print('Socket TCP to LEADER closed')
            exit(0)


def attentRequestTCP():

    global LEADERsock
    print('Thread:', threading.current_thread().getName(), 'with identifier:', threading.current_thread().ident)
    while _connected:
        print("waiting InfoNode...")
        conectionsock, addr=LEADERsock.attendSock()
        t = threading.Thread(name=" Reception info Node", target=RecvInfoNode,args=(conectionsock,addr), daemon=True)
        t.start()


def RecvInfoNode(ConnectSock,addr):
    global node_info, LEADERsock, oncetime
    print('Thread:', threading.current_thread().getName(), 'with identifier:', threading.current_thread().ident)
    while _connected:
        node_info_recv= LEADERsock.ReadSock(ConnectSock,)
        print("data received from:",addr)
        try:
            node_info_recv=eval(node_info_recv)
            #print("InfoNode Recived:", node_info_recv, type(node_info_recv))
        # Proccessing Received Info
            ProccesData(ConnectSock,node_info_recv)

        except Exception as ex:
            print(" data reception no valid. AGENT:",addr[0], "is OUT")
        #check AGENT rol from DDBB
            PARAMS = "selec={'myIP':" + "'" + addr[0] + "'}"
            API_addr_get = 'http://' + node_info['leaderIP'] + ':8000/get_topoDB'
            response = (requests.get(API_addr_get, PARAMS)).json()
            node_info_AGENT = json.loads(response[0])[0]
        # remove AGENT to globlaDB
            PARAMS = "index={'myIP':" + "'" + addr[0] + "'}"
            API_addr_del = 'http://' + node_info['leaderIP'] + ':8000/del_topoDB'
            response = (requests.get(API_addr_del, PARAMS)).json()
        # Select new BACKUP AGENT
            if node_info_AGENT['role']=='BKUPGENT':
                oncetime=1
                print("Selecting new BKUPGENT.....")
                ProccesData(ConnectSock,node_info_recv)
            exit(0)

def receiverUDP():
    global sockrcv,ownrole,node_info,AGENTsockExist, AGENTsock, _AGENTconnected,localDB
    ownrole = node_info['role']
    #identify receiver threads
    print('Thread:',threading.current_thread().getName(),'with identifier:',threading.current_thread().ident)
    sockrcv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockrcv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockrcv.bind((node_info['BcastIP'], int(node_info['portUDP'])))
    print('Listening for datagrams at {}'.format(sockrcv.getsockname()))
    while _AGENTconnected:
        try:
            #receiving data and transmitter address
            data,address=sockrcv.recvfrom(BUFSIZE)
            # decoding and  split tupla
            data= data.decode('ascii')
            node_info_recv=eval(data)
            print(("received data"))
            if node_info['leaderIP'] != node_info_recv['leaderIP']:
                node_info['leaderIP']=node_info_recv['leaderIP']
                node_info['BcastIP'] = node_info_recv['BcastIP']
                node_info['myIP']=getmyIP(node_info)
                localDB.update(node_info)
                if not AGENTsockExist:
                    AGENTsock = socketTCP(node_info)
                    connecAGENTsock = AGENTsock.CreateAGENTSock()
                    # waiting to read info from LEADER
                    run = threading.Thread(name=" AGENT attend TCP Socket", target=AGENTattended,
                                           args=(connecAGENTsock,), daemon=True)
                    run.start()
                    AGENTsockExist = True
                else:
                    AGENTsock.CloseSock()
                    AGENTsockExist = False
                    exit(0)


            # TODO: Updating  localDB with my @IP, @Leader, IoT according Type

            #print("send AGENT info to LEADER:", node_info)
            AGENTsock.WriteSock(connecAGENTsock,node_info)

        except Exception as ex:
            cp.eprint(ex)
# AGENT no connected.close UDP socket
    sockrcv.close()

def ProccesData(socketTCP,node_info_recv=None):
    global oncetime, upt_lock,count,node_info,LEADERsock,localDB
    global checkAddr # definimos checkAddr como global para poder utilizarla en el transmitter

    if node_info['role'] == 'LEADER':
        if node_info_recv != None:
            updt=updattingDB(node_info_recv)


        with upt_lock:
            if (oncetime == 1):
                sleep(3)
                print("conection LEADER to BKUPGENT")
                LEADERToBKUPGENT(socketTCP)
                oncetime = 0

    elif ((node_info_recv['role'] == 'BKUPGENT') and (node_info['myIP']==node_info_recv['myIP'])):
        node_info=node_info_recv
        print("selected as a BKUPGENT. LEADER Ip:", node_info_recv['leaderIP'])
        print('Keepalive....')
        localDB.reset()
        localDB.update(node_info)


    elif node_info['role']== 'BKUPGENT':
        print('Keepalive....')

    elif node_info['role'] == 'AGENT':
        print('AGENT Im')


def IoTset(node_info):
    if node_info['device'] == 'AMB':
        IoT = IoT_AMB
    elif node_info['device'] == 'BOM':
        IoT = IoT_BOM
    elif node_info['device'] == 'CAR':
        IoT = IoT_CAR
    elif node_info['device'] == 'BUI_F':
        IoT = IoT_BUI_F
    elif node_info['device'] == 'BUI_I':
        IoT = IoT_BUI_I
    elif node_info['device'] == 'BUI_J':
        IoT = IoT_BUI_J
    elif node_info['device'] == 'SEM':
        IoT = IoT_SEM
    else:
        IoT=None
    node_info['IoT'] = IoT
    return node_info

def updattingDB (node_info):

## update topo Data Base if AGENT is a new node
    # Add IoT components
    try:
               # request API post to topoDB
        API_addr_update = 'http://' + node_info['leaderIP'] + ':8000/update_topoDB'
        response = (requests.post(API_addr_update, data=node_info))
    except Exception as ex:
        exit(0)
    return True

def LEADERToBKUPGENT(socketTCP):

    global ipBKUPGENT,node_info,LEADERsock
    # select BKUPGENT. Avoid select itself as BKUPGENT
    node_info_back = selectBKUPGENT()
    while (node_info['myIP']==node_info_back['myIP']):
        node_info_back= selectBKUPGENT()
    node_info_back['role']='BKUPGENT'
    #node_info_back['portTCP']=int(node_info['portTCP'])
    print("BKUPGENT:", node_info_back['myIP'])
    #update globalDB
    updattingDB(node_info_back)
    #send flag to notify to AGENT that it is a BKUPGENT
    LEADERsock.WriteSock(socketTCP,node_info_back)

def selectBKUPGENT():
    # algorithm to select a AGENT as a BKUPGENT
    response=['[]']
    PARAMS = "selec={'role':" + "'" + 'AGENT' + "'}"
    print("Waiting for BACKUP........")
    while response[0] == '[]':
        API_addr_get = 'http://' + node_info['myIP'] + ':8000/get_topoDB'
        response = (requests.get(API_addr_get, PARAMS)).json()

    agent = json.loads(response[0])[0]
    del agent['_id']
    return agent

def refresh ():
    global node_info, _connected
    while _connected:
        print('** sending status refresh as:',node_info['role'])
        sleep(10)
        transmitterUDP(node_info)

###############################################
#                   Interface
###############################################
#TODO: possible remove setup
def setup(n_info, ip_cbk=None, role_cbk=None, verbose=False):
    global _role, _type, _BcastIP,_portUDP,portTCP, _nodeID, __setup_done__, cp, _ip_cbk, _role_cbk, node_info
    node_info=n_info
    _role = node_info['role']
    _type = node_info['device']
    _BcastIP = node_info['BcastIP']
    _nodeID = node_info['node_ID']
    if node_info['portUDP'] =='None':
       node_info['portUDP']=portUDP
    if node_info['portTCP'] =='None':
       node_info['portTCP']=portTCP
    _ip_cbk = ip_cbk
    _role_cbk = role_cbk
    cp = custom_print(verbose,_tag)

    __setup_done__ = True
    return node_info


def start(n_info):
    global _connected, thread_module, node_info
    node_info=n_info
    """if not __setup_done__:
        setup(node_info)"""
    _connected = True

    print('Module started')
    thread_module = threading.Thread(target=th_module, daemon=True)
    thread_module.start()
    return _connected


def stop():
    global _connected, thread_module
    _connected = False
    if thread_module is not None:
        thread_module.join()
    if cp is not None:
        print('Module stoped')

