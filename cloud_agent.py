#!/usr/bin/python3
# Cloud Agent Module

#### Imports
import threading, socket, queue
from common import bcolors, custom_print, sendTo
from time import time

#### Private variables
__setup_done__ = False
cp = None
_tag = bcolors.HEADER+'CLOUD'+bcolors.ENDC

#### Global variables
_connected = False

serverPort = 27015
serverSocket = None
id_client = 0

thread_module = None


###############################################
#                   Threads
###############################################

def th_module():
    global _connected

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
    global fire_time, res_fire
    tag = bcolors.OKBLUE + '[client'+str(id)+']: ' + bcolors.ENDC
    cp.vprint(tag + 'Started')

    try:
        # Recive msg from client
        msg = (clientSocket.recvfrom(2048))[0].decode('utf-8')
        cp.vprint(tag + 'recv msg \''+msg+'\'')
        if type(eval(msg)) is tuple:
            t = eval(msg)
            if t.__len__() > 1:
                if t[1] == 'FIRE':
                    fire_time = time()
                    cp.vprint(tag + 'FIRE DETECTED AT '+ str(fire_time))
                elif t[1] == 'FIRED':
                    res_fire = time()
                    elapsed_time = res_fire - fire_time
                    cp.vprint(tag + 'FIRE SOLVED AT ' + str(res_fire))
                    cp.vprint(tag + 'TIME TO SOLVE THE FIRE: '+str(elapsed_time))


    except Exception as ex:
        cp.eprint(bcolors.FAILH + 'ERROR' + bcolors.ENDCH + 'Connection lost...')
        cp.eprint(ex)
        return
    finally:
        clientSocket.close()

    cp.vprint(tag + 'Stoped')
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
    # thread_proc = threading.Thread(target=th_processing,daemon=True)


def startThreads():
    global _connected
    try:
        # thread_proc.start()
        thread_recv.start()
    except Exception as ex:
        cp.eprint(bcolors.FAILH + 'ERROR' + bcolors.ENDCH + 'Thread can not start.')
        cp.eprint(ex)
        _connected = False


###############################################
#                   Interface
###############################################

def setup(verbose=False):
    global __setup_done__, cp
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
    if cp is not None:
        cp.vprint('Module stoped')
    _connected = False
    if thread_module is not None:
        thread_module.join()

if __name__ == '__main__':
    setup(True)
    start()
    msg = input()
    if str(msg).lower() == 'exit':
        stop()