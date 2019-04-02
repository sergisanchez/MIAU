#!/usr/bin/python3
# Device template

####
#   This code is a template for create and integrate a sensor or a device into the testbed
#   The main idea is to code here all the procesing and send the status to the upper class
#   and recv actions.
#
#   HOW TO USE:
#   TODO: todo
#
###

## DO NOI TOUCH THIS PART ##
#### Imports
import threading, socket, queue
from time import sleep

#### Private variables
__setup_done__ = False

#### Global variables
_connected = False
thread_module = None
_status_cbk = None
_id_device = None
_action_queue = queue.Queue()

sem_color = 'GREEN'
congested = False
manualChange = False
rpi_gpio_enabled = True
if rpi_gpio_enabled:
    import RPi.GPIO as GPIO     # LED control GPIO
    GPIO.cleanup()
R = 17
Y = 22
G = 27
B = 23

PORT_IN = 6510

###############################################
#                   Threads
#       Put here all the threads you want to create
###############################################

def th_module():
    # Add here functions that must be executed before the wait loop
    global _connected

    #1. Create all the threads
    threadingSetup()

    #2. Start threads
    startThreads()

    #3. Wait loop
    while _connected:
        pass


def th_ActionReceiver():
    global _connected

    while _connected:
        doAction(_action_queue.get())


def th_processing():
    global congested
    while _connected:
        # Do some processing here
        changeLEDColor()
        sendStatus(sem_color)
        if congested:
            sleep(30)
            congested = False
        sleep(5)



###############################################
#                   Functions
#       Put here all the functions you want to create
###############################################

def threadingSetup():
    # Put here all the threads the device will have.
    # Declare the variable name containing the thread as global
    global thread_recv, thread_proc

    thread_recv = threading.Thread(target=th_ActionReceiver, daemon=True)
    thread_proc = threading.Thread(target=th_processing, daemon=True)


def startThreads():
    global _connected
    # Start here all the threads that needs to be executed at the beginning
    try:
        thread_recv.start()
        thread_proc.start()
    except Exception as ex:
        print('ERROR: Can\'t execute the threads. Finishing the device execution.')
        print(ex)
        _connected = False


def doAction(action):
    global _connected, congested, sem_color
    # Code here the actions the device can interpret
    if action == 'exit':
        _connected = False
    elif action == 'GREEN' or action == 'RED' or action == 'BLUE' or action == 'BLUERED' or action == 'BLUEGREEN':
        congested = True
        sem_color = action
        sendStatus(action)
        changeLEDColor()
    else:
        # Default action
        pass


def changeLEDColor():
    global sem_color
    if congested:
        sem_color = sem_color
    elif sem_color is 'RED':
        # pass      # Si se quiere mantener en RED el semaforo
        sem_color = 'GREEN'
    elif sem_color is 'GREEN':
        sem_color = 'YELLOW'
    else:
        sem_color = 'RED'

    if rpi_gpio_enabled:
        if sem_color == 'RED':
            # Change led to UP
            GPIO.output(R, GPIO.HIGH)
            GPIO.output(Y, GPIO.LOW)
            GPIO.output(B, GPIO.LOW)
            GPIO.output(G, GPIO.LOW)
        elif sem_color == 'GREEN':
            # Change led to DOWN
            GPIO.output(R, GPIO.LOW)
            GPIO.output(Y, GPIO.LOW)
            GPIO.output(B, GPIO.LOW)
            GPIO.output(G, GPIO.HIGH)
        elif sem_color == 'YELLOW':
            GPIO.output(R, GPIO.LOW)
            GPIO.output(Y, GPIO.HIGH)
            GPIO.output(B, GPIO.LOW)
            GPIO.output(G, GPIO.LOW)
        elif sem_color == 'BLUE':
            GPIO.output(R, GPIO.LOW)
            GPIO.output(Y, GPIO.LOW)
            GPIO.output(B, GPIO.HIGH)
            GPIO.output(G, GPIO.LOW)
        elif sem_color == 'BLUERED':
            GPIO.output(R, GPIO.HIGH)
            GPIO.output(Y, GPIO.LOW)
            GPIO.output(B, GPIO.HIGH)
            GPIO.output(G, GPIO.LOW)
        elif sem_color == 'BLUEGREEN':
            GPIO.output(R, GPIO.LOW)
            GPIO.output(Y, GPIO.LOW)
            GPIO.output(B, GPIO.HIGH)
            GPIO.output(G, GPIO.HIGH)
    else:
        print(sem_color)


###############################################
#                   Interface
#       Do not touch this part.
###############################################

def sendStatus(status):
    if _status_cbk is not None:
        # Callback
        _status_cbk(_id_device, status)
    else:
        pass


def recvAction(action):
    _action_queue.put(action, block=False)


def setup(status_cbk=None, id_device=None):
    global __setup_done__, _status_cbk, _id_device
    _status_cbk = status_cbk
    _id_device = id_device

    if rpi_gpio_enabled:
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)      # Sistema de numeración de los pings
        GPIO.setup(R, GPIO.OUT)    # Pin GPIO17 (11) out mode
        GPIO.setup(Y, GPIO.OUT)
        GPIO.setup(B, GPIO.OUT)
        GPIO.setup(G, GPIO.OUT)

    __setup_done__ = True


def start():
    global _connected, thread_module
    if not __setup_done__:
        setup()
    _connected = True

    thread_module = threading.Thread(target=th_module,daemon=True)
    thread_module.start()


def stop():
    global _connected, thread_module
    _connected = False
    if rpi_gpio_enabled:
        GPIO.cleanup()
    if thread_module is not None:
        thread_module.join()

################# TCP CONNECTION   #######################

class info_recv:
    def __init__(self):
        # instanciamos un objeto para trabajar con el socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # fog = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Con el metodo bind le indicamos que puerto debe escuchar y de que servidor esperar conexiones
        # Es mejor dejarlo en blanco para recibir conexiones externas si es nuestro caso
        self.s.bind(("", PORT_IN))

        # Aceptamos conexiones entrantes con el metodo listen, y ademas aplicamos como parametro
        # El numero de conexiones entrantes que vamos a aceptar
        self.s.listen(1)
        print("Listen Agents by Port:", PORT_IN)

    ###########  SEM RECIVE FROM AGENT  #####################
    def receive_data(self):
        # Recibimos el mensaje, con el metodo recvfrom recibimos datos y como parametro
        # la cantidad de bytes para recibir. decode
        (self.sc, self.addr) = self.s.accept()

        try:
            print('waiting data...')
            data = self.sc.recv(1024).decode('utf-8')
            #print('data received from:', addr[0])
            return  data
        except Exception as ex:
            print('End Data', ex)



if __name__ == '__main__':
    setup()
    start()
    connect = info_recv()
    color=connect.receive_data()
    if color == 'GREEN':
        color='BLUEGREEN'
    recvAction(color)
    try:
        while True:
            sleep(0.1)

    except KeyboardInterrupt:
        GPIO.cleanup()