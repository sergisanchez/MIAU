#!/usr/bin/python3
# CP module

#### Imports
import threading, socket,random
from common import bcolors, custom_print
from time import sleep,time
import SendLeader2CloudDB as sendTopoDB2Cloud
import requests
import json

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
topoDB=list()
localDB=list()
topoFile='topoDBfile' # Topology Data Base
localDBfile='LocalDB'
ipLEADER2=0 # initialazing to localhost to test
flag='LEADER2'
porTCP=27000
oncetime=1# Open only once TCP connection in LEADER1
checkAddr='0.0.0'
count=0

#IoT components ######
IoT_SEM = ('lig')
IoT_AMB =('amb')
IoT_BOM = ('bom')
IoT_CAR = ('cam','sens')
IoT_BUI_F = ('temp')
IoT_BUI_I = ('incl')
IoT_BUI_J = ('jam')
#########################

_connected = False
_role = None
_type = None
_BcastIP = None
_nodeID = None
IoT = None
_port = 10600
thread_module = None
upt_lock=threading.Lock()

###############################################
#                   Threads
###############################################

def th_module():
    global _connected, node_info

    # TODO:reset topoDBfile

    #reset localDBfile
    f = open(localDBfile, 'w')
    f.close()

    # obtaining my IP address

    global myIP, upt_lock

    #myIP = getmyIP()
    #node_info['myIP']=myIP

    # select AGENT/LEADER

    if node_info['role'] == 'LEADER':
        print("running as a LEADER \n")
        node_info['leaderIP']=node_info['myIP']
        #addNetworkAddress('LEADER', myIP)
        run = threading.Thread(name="Transmitt running as a LEADER", target=transmitter, args=(node_info,), daemon=True)
        run.start()
        run.join()

        run = threading.Thread(name="receiv running as a LEADER", target=receiver,
                               daemon=True)
        run.start()
        # Thread to select/connect with a AGENT as a LEADER


        # createChanel2DP()
        # sendIP2DP()

        #### refresh IP LEADER

        fresh = threading.Thread(name="refresh", target=refresh,
                                 daemon=True)
        fresh.start()
    else:
        print("running as a AGENT \n")
        run = threading.Thread(name="receiv running as a AGENT", target=receiver,
                               daemon=True)
        run.start()

    ####Send role to DataPlane

    #comunicateRole2DP(_role)
    #3. Wait loop
    while _connected:
        pass


###############################################
#                   Functions
###############################################



def getmyIP ():
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
    #print("myIP:",address[0])
    sockrcv.close()
    sock.close()
    return address[0]

def createChanel2DP():

    global dp_socket

    dp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print('Sockets to Dataplane ready to start.')

def sendIP2DP ():

    print('Sockets to Dataplane ready to start.')
    dp_socket.connect(('147.83.159.220', port2IP))
    dp_socket.send('Im the LEADER '.encode())
    dp_socket.close()

######### Discovery process  ########################
import leader_discover as discoveryAgent
def discovery(id_key):
    # connect to cloud
    discoveryAgent.init_connection()
    # send node ID
    if discoveryAgent.check2cloud(id_key) == "True":
        print("Agent is Registered")
        return True
    else:
        print("agent Not Registered")
        return False
    # close connection
    discoveryAgent.close_connection()


    return True



def updattingDB (node_info):

    global topoDB
    global upt_lock  # mutex
    #upt_lock=threading.Lock()
## update topo Data Base if AGENT is a new node
    # Add IoT components
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
    node_info['IoT']=IoT
    # request API post to topoDB
    response = (requests.post('http://147.83.159.220:8000/update_topoDB', data=node_info))

    return True


def refresh ():
    global node_info
    while True:
        print('** sending status refresh as:',node_info['role'])
        sleep(10)
        transmitter(node_info)


def transmitter(node_info):
    global start_setuptime,sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    #text = (node_info['device'],node_info['role'],str(node_info['node_ID']))
 ## start setup time counter
    start_setuptime=time()
 # send device and role
    #print("sending to: network=", node_info['BcastIP'],"port=",node_info['port'])
    #sock.sendto((str(text)).encode(), (node_info['BcastIP'], node_info['port']))
    sock.sendto((str(node_info)).encode(), (node_info['BcastIP'], node_info['port']))
    sock.close()


def receiver():
    global sockrcv,ownrole,node_info
    ownrole = node_info['role']
    #identify receiver threads
    print('Thread:',threading.current_thread().getName(),'with identifier:',threading.current_thread().ident)
    sockrcv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockrcv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockrcv.bind((node_info['BcastIP'], int(node_info['port'])))
    print('Listening for datagrams at {}'.format(sockrcv.getsockname()))
    while True:
        try:
            #receiving data and transmitter address
            data,address=sockrcv.recvfrom(BUFSIZE)
            # decoding and  split tupla
            data= data.decode('ascii')
            node_info_recv=eval(data)
            #print(("received data:", node_info_recv))
            #node_info['role']=data[1]
            #node_info['device']=data[0]
            #node_info['node_ID']=data[2]
            node_info['BcastIP']=node_info_recv['BcastIP']

            #print("device updated:",node_info, "Ownrole:", ownrole)
            proc = threading.Thread(name= "ProcData",target=ProccesData, args=(ownrole,node_info_recv),
                                   daemon=True)  # Once socket receives data, processing
            proc.start()
        except Exception as ex:
            cp.eprint(ex)
            break

def ProccesData(yourrole, node_info_recv):
    ##global sockrcv  # used to close connection when AGENT is LEADER
    ###global norecvaddr  # evita que el transmitter arranque antes que el receiver tenga la IP
    global oncetime, upt_lock,count,node_info
    ownrole = yourrole
    global checkAddr # definimos checkAddr como global para poder utilizarla en el transmitter


    #yourole == ownrole
    #if node_info_recv['role'] == 'BKUPGENT':

        #ownrole = node_info['role']
    if node_info['role'] == 'LEADER':

        updt=updattingDB(node_info_recv)
        # Updating  localDB with my @IP, @Leader(myself), IoT according Type
        #TODO: updating localDB
        #updattingLocalDB()
        # Send TopoDB to Cloud
        #run = threading.Thread(name="sendTopoDB2Cloud", target=sendTopoDB2Cloud.run, args=(), daemon=True)
        #run.start()
        # wait to create topoDB and open TCP conection
        #print("oncetime:", oncetime)
        with upt_lock:
            if (oncetime == 1):
                sleep(3)
                print("conection LEADER to BKUPGENT")
                LEADERToBKUPGENT()
                oncetime = 0

    elif ((node_info_recv['role'] == 'BKUPGENT') and (node_info['myIP']==node_info_recv['myIP'])):
        node_info=node_info_recv
        # AGENT has been selected as a BKUPGENT
        print("selected as a BKUPGENT. LEADER Ip:", node_info_recv['leaderIP'])
        #updattingDB(node_info_recv)

        createSocketTCP2LEADER( )




    elif node_info['role'] == 'AGENT':
        #if LEADER is diffrent then send again id info to new LEADER

        #if node_info['leaderIP'] != node_info_recv['leaderIP']:

        node_info['leaderIP'] = node_info_recv['leaderIP']
        #print('Sending id info to the LEADER:', node_info)
        # TODO: Updating  localDB with my @IP, @Leader, IoT according Type
            #updattingLocalDB(getmyIP(), address, _type)

        # send agent info to leader
        run = threading.Thread(name="transmitter AGENT",target=transmitter,args=(node_info,), daemon=True)
        run.start()
        count=0
        """else:
            # AGENT keepalive
            if count == 10:
                # send agent info to leader
                print('sending keepalive AGENT... ')
                run = threading.Thread(name="transmitter keepalive AGENT", target=transmitter, daemon=True)
                run.start()
                count=0
            count=count+1"""







def selectBKUPGENT():
    # algorithm to select a AGENT as a BKUPGENT
    response=['[]']
    PARAMS = "selec={'role':" + "'" + 'AGENT' + "'}"
    print("Waiting for BACKUP........")
    while response[0] == '[]':
        response = (requests.get('http://147.83.159.220:8000/get_topoDB', PARAMS)).json()

    agent = json.loads(response[0])[0]
    del agent['_id']
    return agent




def createSocketTCP2BKUPGENT():
    global node_info
    print("Open TCP connection in LEADER to BKUPGENT ")
    try:
        # Create socket and listen
        LEADER_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # listening
            # the SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state,
            # without waiting for its natural timeout to expire
        LEADER_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
             # Specify the welcoming port to receive
        LEADER_socket.bind(('', porTCP))
        print('OK Connection created.')
        LEADER_socket.listen(1)

        while True:
            LEADER_socket.accept()
            pass

    except Exception as ex:
        print('Unable to connect to BKUPGENT')
        print(ex)
    #finally:
        # Close the connection
     #   LEADER_socket.close()

def createSocketTCP2LEADER():

    global oncetime,node_info
    while True:
        sleep(3)

        try:
            # Connect and send keepalive
            BKUPGENT_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            BKUPGENT_socket.connect((node_info['leaderIP'],porTCP))
            print("KeepAlive to the LEADER IP:", node_info['leaderIP'])
        except Exception as ex:
            print('Unable to connect to the LEADER')
            cp.eprint(ex)
            #close receiver socket as AGENT
            sockrcv.close()
            #close transmitter socket as AGENT
            sock.close()
            ### swich to LEADER
            oncetime = 1  # Open only once TCP connection in LEADER
            # send broadcast to AGENTs
            #comunicateRole2DP('LEADER')
            #print("Send LEADER info")
            ownrole = 'LEADER'
            # remove failed leader to globlaDB
            PARAMS = "index={'myIP':" + "'" + node_info['leaderIP'] + "'}"
            response = (requests.get('http://147.83.159.220:8000/del_topoDB', PARAMS)).json()
            # update info new leader
            node_info['role']='LEADER'
            node_info['leaderIP']=node_info['myIP']
            print ("I'm new leader:", node_info)
            updattingDB(node_info)

            #comunicateRole('LEADER')
            run = threading.Thread(name="Send LEADER info",target=transmitter(node_info,), daemon=True)
            run.start()
            #run.join()
            print("Receive as new LEADER")
            run = threading.Thread(name="receivernewLEADER",target=receiver, daemon=True)
            run.start()
            #### refresh IP LEADER

            fresh = threading.Thread(name="refresh", target=refresh,
                                     daemon=True)
            fresh.start()
            exit(0)

        finally:
            # Close the connection
           BKUPGENT_socket.close()

def LEADERToBKUPGENT():
    global ipBKUPGENT,node_info
    # select BKUPGENT. Avoid select itself as BKUPGENT
    node_info_back = selectBKUPGENT()
    while (node_info['myIP']==node_info_back['myIP']):
        node_info_back= selectBKUPGENT()
    node_info_back['role']='BKUPGENT'
    node_info_back['port']=int(node_info['port'])
    print("BKUPGENT:", node_info_back)
    #update globalDB
    updattingDB(node_info_back)
    #send flag to notify to AGENT that it is a BKUPGENT
    run = threading.Thread(name="send flag 2AGENTasBKUPGENT",target=transmitter, args=(node_info_back,), daemon=True)
    run.start()
    run.join()
    # Create socket TCP to BKUPGENT args=(ipBKUPGENT,porTCP)
    run = threading.Thread(name="Create socket TCP to BKUPGENT",target=createSocketTCP2BKUPGENT, daemon=True)
    run.start()





def requestNetworkAddresses(key):
    if _ip_cbk is not None:
        return _ip_cbk(key=key)[key]
    else:
        return ''


def addNetworkAddress(key, value):
    if _ip_cbk is not None:
        _ip_cbk(write=True, key=key, value=value)


def comunicateRole2DP(role):
    if _role_cbk is not None:
        _role_cbk(role)

def updattingLocalDB():
    global localDB,node_info
    #leaderIP = eval(leaderIP)
    #print("Tipo: ",type(leaderIP))
    # Add IoT components
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
    node_info['IoT'] = IoT

    #DB = open(localDBfile, 'w')
    if not ((node_info['myIP'],node_info['leaderIP'], node_info['IoT']) in localDB):
        print("Updating LocalDB \n")
        localDB.append((node_info['myIP'],node_info['leaderIP'], node_info['IoT']))
        s = str(node_info['myIP'],node_info['leaderIP'], node_info['IoT'])
        DB = open(localDBfile, 'w')
        DB.write(s)
        DB.write('\n')
        DB.close()

###############################################
#                   Interface
###############################################
#TODO: possible remove setup
def setup(n_info, ip_cbk=None, role_cbk=None, verbose=False):
    global _role, _type, _BcastIP,_port, _nodeID, __setup_done__, cp, _ip_cbk, _role_cbk, node_info
    node_info=n_info
    _role = node_info['role']
    _type = node_info['device']
    _BcastIP = node_info['BcastIP']
    _nodeID = node_info['node_ID']
    if node_info['port'] =='None':
       node_info['port']=_port
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

