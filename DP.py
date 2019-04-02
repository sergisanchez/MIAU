#!/usr/bin/python3
# DP module

#### Imports
import threading, socket, queue
from common import bcolors, custom_print, sendTo
from random import randint
import APP_fire as app


#### Private variables
__setup_done__ = False
cp = None
_tag = bcolors.HEADER+'DP'+bcolors.ENDC
_ip_cbk = None
_result_queue = queue.Queue()
ip_status_devices_lock = threading.Lock()


#### Global variables
_connected = False
_role = None


serverPort = 27015
serverSocket = None
id_client = 0

ip_status_devices = {} # ip:(ip,type,status)
ip_nodes = {}


thread_module = None
thread_recv = None
thread_proc = None


###############################################
#                   Threads
###############################################

def th_module():
    global _connected
    #0. Wait until the role has been set
    while _role is None:
        pass

    #1. Create all the threads
    createServer()
    threadingSetup()

    #2. Start threads
    startThreads()

    #3. Wait loop
    while _connected:
        pass


def th_receiver():
    tag = bcolors.OKBLUE + '[recv]: ' + bcolors.ENDC
    cp.vprint(tag + 'Started receiver module')
    global serverSocket
    global id_client

    # Listen for new connections
    serverSocket.listen(1)
    while _connected:
        try:
            (connectionsocket, clientAddress) = serverSocket.accept()
            cp.vprint(tag + 'New connection - ' + str(clientAddress))
            # Create new thread for each new connection
            t = threading.Thread(target=th_client, args=(id_client, clientAddress[0], connectionsocket))
            t.start()
            id_client += 1
        except Exception as excep:
            cp.eprint(bcolors.FAILH + 'ERROR' + bcolors.ENDCH + 'Welcome fail')
            cp.eprint(excep)
            return

    cp.vprint(tag + 'Stoped receiver module')
    return


def th_client(id, clientAddress, clientSocket):
    tag = bcolors.OKBLUE + '[client'+str(id)+']: ' + bcolors.ENDC
    cp.vprint(tag + 'Started')

    try:
        # Recive msg from client
        msg = (clientSocket.recvfrom(2048))[0].decode('utf-8')
        cp.vprint(tag + 'recv msg \''+msg+'\'')
        performMessage(msg, clientAddress, tag=tag, csocket=clientSocket)
    except Exception as ex:
        cp.eprint(bcolors.FAILH + 'ERROR' + bcolors.ENDCH + 'Connection lost...')
        cp.eprint(ex)
        return
    finally:
        clientSocket.close()

    cp.vprint(tag + 'Stoped')
    return


def th_processing():
    tag = bcolors.OKBLUE + '[proc]: ' + bcolors.ENDC
    cp.vprint(tag + 'Started processing module')
    congested = False
    status_save = congested

    while _connected:
        # carcount = 0
        # stopcount = 0
        # minstops = 10
        # with ip_status_devices_lock:
        #     ldev = ip_status_devices.values()
        # for node in ldev:
        #     if type(node) is not tuple or node.__len__() != 3:
        #         pass
        #     else:
        #         if str(node[1]).lower() == 'CAR'.lower():
        #             carcount += 1
        #             if str(node[2]).lower() == 'STOP'.lower():
        #                 stopcount += 1
        #
        # if stopcount > carcount/2 and carcount >= minstops:
        #     # Cogestion detected
        #     congested = True
        # else:
        #     # Congestion not detected
        #     congested = False
        #
        # if status_save != congested and congested:
        #     searchFogAndExecuteAPPCongestion()
        # status_save = congested
        pass

    cp.vprint(tag + 'Stoped processing module')
    return


###############################################
#                   Functions
###############################################

def createServer():
    global serverPort, serverSocket

    # Server Set-up
    try:
        # Setup IPv4 TCP socket
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # the SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state,
        # without waiting for its natural timeout to expire
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Specify the welcoming port of the server
        serverSocket.bind(('', serverPort))
        cp.vprint(bcolors.OKGREENH+'OK'+bcolors.ENDCH+'Server created.')
    except Exception as ex:
        cp.eprint(bcolors.FAILH + 'ERROR' + bcolors.ENDCH + 'Can\'t create the socket. '
                                                        'Maybe you have another server at the same port?')
        cp.eprint(ex)
        exit(-1)


def threadingSetup():
    global thread_recv, thread_proc
    thread_recv = threading.Thread(target=th_receiver,daemon=True)
    thread_proc = threading.Thread(target=th_processing,daemon=True)


def startThreads():
    global _connected
    try:
        thread_proc.start()
        thread_recv.start()
    except Exception as ex:
        cp.eprint(bcolors.FAILH + 'ERROR' + bcolors.ENDCH + 'Thread can not start.')
        cp.eprint(ex)
        _connected = False


def requestNetworkAddresses(key):
    if _ip_cbk is not None:
        return _ip_cbk(key=key)[key]
    else:
        return ''


def addNetworkAddress(key, value):
    if _ip_cbk is not None:
        _ip_cbk(write=True, key=key, value=value)


def performMessage(msg, clientAddress, tag='', csocket=None):
    if _role == 'SA':
        if msg == 'RED' or msg == 'GREEN':
            updateDeviceDBStatus(clientAddress, msg)
            forwardMessageToCloud(clientAddress,msg)
        elif msg == 'START' or msg == 'STOP':
            updateDeviceDBStatus(clientAddress, msg)
            forwardMessageToCloud(clientAddress,msg)
        elif msg == 'CONGESTED' or msg == 'FIRE_I':
            if csocket is not None:
                # Send to fog the IP nodes
                with ip_status_devices_lock:
                    csocket.send(str(list(ip_status_devices.values())).encode())
            # cp.vprint(tag + bcolors.OKGREENH + 'CONGESTED recived from cloud. Congestion problem.' + bcolors.ENDC)
            # congested = True
        elif msg == 'NO CONGESTED':
            # cp.vprint(tag+bcolors.OKGREENH+'NO CONGESTED recived from cloud. Congestion solved.'+bcolors.ENDC)
            # congested = False
            pass
        elif msg == 'FIRE':
            searchFogAndExecuteAPPFire(clientAddress)
            forwardMessageToCloud(clientAddress, msg)

        forwardMessageToFrontend(clientAddress,msg)
    elif _role == 'MA':
        if app.isRecognized(msg):
            app.start((requestNetworkAddresses('SA'),27015), msg='', result_cbk=recvResult)


def forwardMessageToFrontend(addr, msg):
    cp.vprint('Send to frontend: \''+str(((addr, msg),))+'\'')
    sendTo(
        (requestNetworkAddresses('frontend'), 27015),
        msg=str(((addr, msg),(requestNetworkAddresses('SA'),'sa')))
    )


def forwardMessageToCloud(addr, msg):
    # TODO: mejorar esta cosa
    cp.vprint('Send to cloud: \'' + str(((addr, msg),)) + '\'')
    sendTo((requestNetworkAddresses('cloud'), 27015), msg=str(((addr, msg),)))


def searchFogAndExecuteAPPCongestion(selfdev_addr):
    with ip_status_devices_lock:
        if list(ip_status_devices.keys()).__len__() == 0:
            return
        done = False
        while not done:
            ip_fog = list(ip_status_devices.keys())[randint(0,list(ip_status_devices.keys()).__len__()-1)]
            if ip_fog != requestNetworkAddresses('SA'):
                if (selfdev_addr is not None and selfdev_addr != ip_fog) or selfdev_addr is None:
                    done = True

    sendTo((ip_fog,27015),msg='CONGESTED')


def searchFogAndExecuteAPPFire(selfdev_addr):
    ip_fog = ''
    with ip_status_devices_lock:
        if list(ip_status_devices.keys()).__len__() == 0:
            return
        done = False
        while not done:
            ip_fog = list(ip_status_devices.keys())[randint(0, list(ip_status_devices.keys()).__len__() - 1)]
            if ip_fog != requestNetworkAddresses('SA'):
                if (selfdev_addr is not None and selfdev_addr != ip_fog) or selfdev_addr is None:
                    done = True

    sendTo((ip_fog, 27015), msg='FIRE')
    forwardMessageToFrontend(ip_fog, 'ma')


def updateDeviceDBStatus(id_dev, status):
    if id_dev in ip_status_devices.keys():
        # Update the value
        cp.vprint('Status from ' + id_dev + ' it\'s now ' + status)
        with ip_status_devices_lock:
            ip_status_devices[id_dev] = status
    else:
        # If not registred, add the device
        cp.vprint('New device registred from ' + id_dev + ' with status ' + status)
        with ip_status_devices_lock:
            ip_status_devices[id_dev] = status


def recvResult(result):
    _result_queue.put(result, block=False) # TODO: Useless
    forwardMessageToCloud(requestNetworkAddresses('SA'),'FIRED')


###############################################
#                   Interface
###############################################

def swapRole(role):
    global _role
    _role = role


def setup(ip_cbk=None, verbose=False):
    global __setup_done__, cp, _ip_cbk
    _ip_cbk = ip_cbk
    cp = custom_print(verbose,_tag)

    __setup_done__ = True


def start():
    global _connected, thread_module
    if not __setup_done__:
        setup()
    _connected = True

    cp.vprint('Module started')
    thread_module = threading.Thread(target=th_module,daemon=True)
    thread_module.start()


def stop():
    global _connected, thread_module
    _connected = False
    app.stop()
    if thread_module is not None:
        thread_module.join()
    if cp is not None:
        cp.vprint('Module stoped')


