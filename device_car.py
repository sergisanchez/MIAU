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
from common import bcolors

#### Private variables
__setup_done__ = False

#### Global variables
_connected = False
thread_module = None
_status_cbk = None
_id_device = None
_action_queue = queue.Queue()

car_status = 'STOP'
rpi_gpio_enabled = False

if rpi_gpio_enabled:
    import coche
    car = coche.cotxe()
else:
    print(bcolors.WARNINGH + 'INFO' + bcolors.ENDCH +
          'GPIO not enabled. Modules not loaded!')


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
    if not rpi_gpio_enabled:
        print(bcolors.WARNING + 'GPIO not enabled. '
                                'The car will not move. '
                                'Only prints the status.'
              + bcolors.ENDC)
    else:
        car.arranca(30)

    andavant = False
    while _connected:
        # Do some processing here
        if not rpi_gpio_enabled:
            if car_status == "START" and not andavant:
                print('Car is ' + bcolors.WARNING + car_status + bcolors.ENDC)
                andavant = True
                sendStatus(car_status)
            elif car_status == "STOP" and andavant:
                print('Car is ' + bcolors.WARNING + car_status + bcolors.ENDC)
                andavant = False
                sendStatus(car_status)
        else:
            if car_status == "START" and not andavant:
                car.andavant()
                andavant = True
                sendStatus(car_status)
            elif car_status == "STOP" and andavant:
                andavant = False
                car.frena()
                sendStatus(car_status)

    if rpi_gpio_enabled:
        car.apagar()


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
    global _connected, car_status
    # Code here the actions the device can interpret
    if action == 'exit':
        _connected = False
    elif action == 'GREEN':
        car_status = 'START'
    elif action == 'RED':
        car_status = 'STOP'
    else:
        # Default action
        pass


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
    if thread_module is not None:
        thread_module.join()

