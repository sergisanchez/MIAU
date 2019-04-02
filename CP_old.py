#!/usr/bin/python3
# CP module

#### Imports
import threading, socket,random
from common import bcolors, custom_print
from time import sleep,time
import SendLeader2CloudDB as sendTopoDB2Cloud
import requests
import json

#### Private variables
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
_host = None
_nodeID = None
IoT = None
_port = 10600
thread_module = None


###############################################
#                   Threads
###############################################

def th_module():
    global _connected

    # reset topoDBfile
    f = open(topoFile, 'w')
    f.close()
    #reset localDBfile
    f = open(localDBfile, 'w')
    f.close()

    # obtaining my IP address

    global myIP, upt_lock
    myIP = getmyIP()

    # mutex

    upt_lock = threading.Lock()

    # select AGENT/LEADER

    if _role == 'LEADER':
        cp.vprint("running as a LEADER \n")
        #addNetworkAddress('LEADER', myIP)
        run = threading.Thread(name="Transmitt running as a LEADER", target=transmitter,
                               args=(_type, _role, _nodeID, _host, _port), daemon=True)
        run.start()
        run.join()
        run = threading.Thread(name="receiv running as a LEADER", target=receiver, args=(_role, "", _port),
                               daemon=True)
        run.start()
        # Thread to select/connect with a AGENT as a LEADER


        # createChanel2DP()
        # sendIP2DP()

        #### refresh IP LEADER

        fresh = threading.Thread(name="refresh", target=refresh, args=(_type, _role, _host, _port),
                                 daemon=True)
        fresh.start()
    else:
        cp.vprint("running as a AGENT \n")
        run = threading.Thread(name="receiv running as a AGENT", target=receiver, args=(_role, "", _port),
                               daemon=True)
        run.start()

    ####Send role to DataPlane

    comunicateRole2DP(_role)
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
    #cp.vprint(address[0])
    sockrcv.close()
    sock.close()
    return address[0]

def createChanel2DP():

    global dp_socket

    dp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    cp.vprint('Sockets to Dataplane ready to start.')

def sendIP2DP ():

    cp.vprint('Sockets to Dataplane ready to start.')
    dp_socket.connect(('localhost', port2IP))
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



def updattingDB (info_node):

    global topoDB
    global upt_lock  # mutex
    #upt_lock=threading.Lock()
## update topo Data Base if AGENT is a new node
    # Add IoT components
    if info_node['device'] == 'AMB':
        IoT = IoT_AMB
    elif info_node['device'] == 'BOM':
        IoT = IoT_BOM
    elif info_node['device'] == 'CAR':
        IoT = IoT_CAR
    elif info_node['device'] == 'BUI_F':
        IoT = IoT_BUI_F
    elif info_node['device'] == 'BUI_I':
        IoT = IoT_BUI_I
    elif info_node['device'] == 'BUI_J':
        IoT = IoT_BUI_J
    elif info_node['device'] == 'SEM':
        IoT = IoT_SEM
    info_node['IoT']=IoT

# request API Update database if data exists, else post a new document

    response = (requests.post('http://147.83.159.220:8000/update_topoDB', data=info_node))

    return True


def refresh (device,role,network, port):
    while True:
        cp.vprint('** sending status refresh as:',role)
        sleep(10)
        transmitter(device,role,_nodeID,network, port)


def transmitter(device, role, nodeID, network, port):
    global start_setuptime,sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    text = (device,role,str(nodeID))
 ## start setup time counter
    start_setuptime=time()
 # send device and role
    sock.sendto((str(text)).encode(), (network, port))
    sock.close()


def receiver(yourrole,interface, port):
    global sockrcv,ownrole
    ownrole = yourrole
    #identify receiver threads
    cp.vprint('Thread:',threading.current_thread().getName(),'with identifier:',threading.current_thread().ident)
    sockrcv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockrcv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockrcv.bind((interface, port))
    cp.vprint('Listening for datagrams at {}'.format(sockrcv.getsockname()))
    while True:
        try:
            #receiving data and transmitter address
            data,address=sockrcv.recvfrom(BUFSIZE)
            # decoding and  split tupla
            data= data.decode('ascii')
            data=eval(data)
            role=data[1]
            device=data[0]
            nodeID=data[2]

            cp.vprint("device received:", device, "IP:", address[0],"Ownrole:", ownrole, "Role:", role, 'ID', nodeID)
            proc = threading.Thread(name= "ProcData",target=ProccesData, args=(ownrole,role,device,nodeID,address),
                                   daemon=True)  # Once socket receives data, processing
            proc.start()
        except Exception as ex:
            cp.eprint(ex)
            break

def ProccesData(yourrole, role, device, nodeID, address):
    ##global sockrcv  # used to close connection when AGENT is LEADER1
    ###global norecvaddr  # evita que el transmitter arranque antes que el receiver tenga la IP
    global oncetime
    ownrole = yourrole


    global checkAddr  # definimos checkAddr como global para poder utilizarla en el transmitter
    #yourole == ownrole
    if role == 'LEADER2':

        ownrole = role
    if ownrole == 'LEADER':
        info_leader={'device':device,
                     'role':role,
                     'nodeID':nodeID,
                     'address':address[0]}
        updt=updattingDB(info_leader)
        # Updating  localDB with my @IP, @Leader(myself), IoT according Type
        updattingLocalDB(getmyIP(), (getmyIP(),), _type)
        # Send TopoDB to Cloud
        run = threading.Thread(name="sendTopoDB2Cloud", target=sendTopoDB2Cloud.run, args=(), daemon=True)
        run.start()
        # wait to create topoDB and open TCP conection
        with upt_lock:
            if (oncetime == 1) and updt:
                sleep(3)
                cp.vprint("conection LEADER1 to LEADER2")
                LEADER1ToLEADER2()
                oncetime = 0

    elif ownrole == 'LEADER2':
        # AGENT has been selected as a LEADER2
        cp.vprint("selected as a LEADER2. LEADER1 Ip:", address[0])

        createSocketTCP2LEADER1(address[0],)




    elif ownrole == 'AGENT':
        # if LEADER is diffrent then send again id info to new LEADER
        #if address[0] != checkAddr:
        checkAddr = address[0]
        cp.vprint('Sending id info to the LEADER: ' + checkAddr)
        # Updating  localDB with my @IP, @Leader, IoT according Type
        updattingLocalDB(getmyIP(), address, _type)

        # transmitter(_type,checkAddr,address[1])
        run = threading.Thread(name="transmitter AGENT",target=transmitter, args=(_type, ownrole, _nodeID, address[0], _port), daemon=True)
        run.start()
            # inform to DP about new LEADER
        addNetworkAddress('LEADER', address[0])
            # run.join()




def selectLEADER2(ipLEADER2=0):
    # algorithm to select a AGENT as a LEADER2
    while ipLEADER2==0:
        lista = list()
        topodb = 'topoDBfile'
        file = open(topodb, 'r')
        with file as topo:
            for node in topo:
                node = eval(node)  # convert string to tuple
                lista.append(node)
                #cp.vprint(lista)
            #while True:
                #select a random 0<= index <= lista lengh
        index = random.randint(0, len(lista) - 1)
        if (lista[index][0] == 'SEM') and (lista[index][3]!=myIP): # chose only SEM
            ipLEADER2=(lista[index][3])
                   # break
        file.close()
    cp.vprint('LEADER2 IP : ',str(ipLEADER2))

    return ipLEADER2

def createSocketTCP2LEADER2(ipLEADER2,porTCP):
    cp.vprint("Open TCP connection in LEADER1 to LEADER2 ")
    try:
        # Create socket and listen
        LEADER_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # listening
            # the SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state,
            # without waiting for its natural timeout to expire
        LEADER_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
             # Specify the welcoming port to receive
        LEADER_socket.bind(('', porTCP))
        cp.vprint('OK Connection created.')
        LEADER_socket.listen(1)
        LEADER_socket.accept()
        while True:
            pass

    except Exception as ex:
        cp.vprint('Unable to connect to LEADER2')
        cp.vprint(ex)
    #finally:
        # Close the connection
     #   LEADER_socket.close()

def createSocketTCP2LEADER1(adrr):

    global oncetime
    while True:
        sleep(3)
        cp.vprint("KeepAlive to the LEADER1 IP:",adrr)
        try:
            # Connect and send keepalive
            LEADER2_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            LEADER2_socket.connect((adrr,porTCP))

        except Exception as ex:
            cp.vprint('Unable to connect to the LEADER1')
            cp.eprint(ex)
            #close receiver socket as AGENT
            sockrcv.close()
            #close transmitter socket as AGENT
            sock.close()
            ### swich to LEADER1
            oncetime = 1  # Open only once TCP connection in LEADER1
            # send broadcast to AGENTs
            comunicateRole2DP('LEADER')
            cp.vprint("Send LEADER info")
            ownrole = 'LEADER'
            comunicateRole2DP('LEADER')
            run = threading.Thread(name="Send LEADER info",target=transmitter, args=(_type,'LEADER', _nodeID, BROADCASTADDR, _port), daemon=True)
            run.start()
            #run.join()
            cp.vprint("Receive as new LEADER")
            run = threading.Thread(name="receivernewLEADER",target=receiver, args=('LEADER', "", _port), daemon=True)
            run.start()
            #### refresh IP LEADER

            fresh = threading.Thread(name="refresh", target=refresh, args=(_type, 'LEADER',BROADCASTADDR, _port),
                                     daemon=True)
            fresh.start()
            exit(0)

        finally:
            # Close the connection
           LEADER2_socket.close()

def LEADER1ToLEADER2():
    global ipLEADER2
    # select LEADER2
    ipLEADER2= selectLEADER2()
    if ipLEADER2 != 0:
        #send flag to notify to AGENT that it is a LEADER2
        run = threading.Thread(name="send flag 2AGENTasLEADER2",target=transmitter, args=(_type,flag, _nodeID, ipLEADER2, _port), daemon=True)
        run.start()
        run.join()
        # Create socket TCP to LEADER2
        run = threading.Thread(name="Create socket TCP to LEADER2",target=createSocketTCP2LEADER2, args=(ipLEADER2,porTCP), daemon=True)
        run.start()
    else:
        cp.eprint("No LEADER2 selected")




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

def updattingLocalDB(ownIP,LeaderIP,type):
    global localDB
    #LeaderIP = eval(LeaderIP)
    #print("Tipo: ",type(LeaderIP))
    # Add IoT components
    if type == 'AMB':
        IoT = IoT_AMB
    elif type == 'BOM':
        IoT = IoT_BOM
    elif type == 'CAR':
        IoT = IoT_CAR
    elif type == 'BUI_F':
        IoT = IoT_BUI_F
    elif type == 'BUI_I':
        IoT = IoT_BUI_I
    elif type == 'BUI_J':
        IoT = IoT_BUI_J
    elif type == 'SEM':
        IoT = IoT_SEM

    #DB = open(localDBfile, 'w')
    if not ((ownIP,LeaderIP[0], IoT) in localDB):
        cp.vprint("Updating LocalDB \n")
        localDB.append((ownIP,LeaderIP[0], IoT))
        s = str((ownIP,LeaderIP[0], IoT))
        DB = open(localDBfile, 'w')
        DB.write(s)
        DB.write('\n')
        DB.close()

###############################################
#                   Interface
###############################################

def setup(role, type, host,port, nodeID, ip_cbk=None, role_cbk=None, verbose=False):
    global _role, _type, _host,_port, _nodeID, __setup_done__, cp, _ip_cbk, _role_cbk
    _role = role
    _type = type
    _host = host
    _nodeID = nodeID
    if port !='None':
       _port=port
    _ip_cbk = ip_cbk
    _role_cbk = role_cbk
    cp = custom_print(verbose,_tag)

    __setup_done__ = True


def start():
    global _connected, thread_module
    if not __setup_done__:
        setup('AGENT', 'SEM', "",'None', '')
    _connected = True

    cp.vprint('Module started')
    thread_module = threading.Thread(target=th_module, daemon=True)
    thread_module.start()


def stop():
    global _connected, thread_module
    _connected = False
    if thread_module is not None:
        thread_module.join()
    if cp is not None:
        cp.vprint('Module stoped')

