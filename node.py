#!/usr/bin/python3
# Node program

# Definition of the program
'''
/*******node.py*******|
*   ________________  |
*  |_______ui_______| |
*   ________________  |
*  |_____RTM.py______| |
*   ________________  |
*  |_____DP.py______| |
*   ________________  |
*  |_____dev.py_____| |
/*********************/
'''

#### Imports
import os, argparse
import threading
from time import sleep
import requests


import RTM as rtm
from common import custom_print
cstp = custom_print(True,'[node.py] ')

def nop():
    pass

#### PID
print('PID: ' + str(os.getpid()))

#### Global Variables
connected = True
thread_RTM = None
parser = argparse.ArgumentParser(description='Node description here')
IP = {'cloud':'192.168.4.77', 'LEADER':'', 'sap':'', 'broadcast':'', 'frontend':'192.168.4.149'}
_file_name = 'id_key.txt'
node_info={
    'device':'None',
    'role':'None',
    'myIP':'None',
    'leaderIP':'None',
    'port':'None',
    'BcastIP':'None',
    'node_ID':'None',
    'IoT':'None'
}


###############################################
#                   Threads
###############################################

def th_RTM(node_info):
    node_info=rtm.setup(node_info, verbose=True, ip_cbk=ipValue)
    node_info['myIP']=rtm.getmyIP()
    connected=rtm.start(node_info)

    while connected:
        nop()

    rtm.stop()


def th_ui():
    global connected
    while connected:
        msg = input('->')
        if str(msg).lower() == 'exit':
            connected = False


###############################################
#                   Functions
###############################################

def threadingSetup(node_info):

    thread_RTM = threading.Thread(target=th_RTM,args=(node_info,), daemon=True)
    thread_RTM.start()



def threadingJoining():
    thread_RTM.join()


def ipValue(write=False, key='', value=''):
    global IP

    if write:
        if key != '':
            IP[key] = value
        else:
            cstp.eprint('ERROR: Operation not allowed. Can not write with an empty key.')
    else:
        # Get/Read some value
        # Return is allways a dictionary
        if key == '':
            # Get all
            return IP.copy()
        elif not key in IP.keys():
            return {key:''}
        else:
            return {key:IP[key]}


def identificationProccess(node_info):
    import random
    nodeID = str(random.randint(0,100000000))
    """#method to obtain a key from cloud
    import obtain_key as registration
    cpath = os.path.join(os.path.abspath(os.path.curdir), _file_name)
    if not os.path.isfile(cpath):
        print("The node don't have an ID")

        # TODO: Registration process here!
        registration.init_connection()
        print("Agent type:",node_info['role'])
        node_id, user_key=registration.send2cloud(args.d)
        _nodeID = (user_key,str(node_id))
        print("New nodeID:",_nodeID)
        registration.close_connection()
        
        try:
            file = open(cpath, 'w')
            file.write(str(_nodeID))
            file.close()
        except Exception as ex:
            cstp.eprint('Error while creating Id file. Exiting...')
            cstp.eprint(ex)
            exit(-1)
    else:
        print("The node has an ID, we  recover")
        try:
            file = open(cpath, 'r')
            #_nodeID = eval(file.read())
            _nodeID = file.read()
            file.close()
        except FileNotFoundError:
            cstp.eprint('Error while opening Id file. Exiting...')
            exit(-1)"""
    return nodeID
###############################################
#                   AGENT in Thread
###############################################

# Args

parser.add_argument('d', metavar='device', default='NONE', help='device: CAR/SEM/AMB/BOM/BUI_F/BUI_I/BUI_J')
parser.add_argument('role', choices={'LEADER': 'LEADER', 'AGENT': 'AGENT'}, help='which role to take')
parser.add_argument('-g', metavar='gpio', type=bool, default=False, help='GPIO enabled')
parser.add_argument('BcastIP', help='interface the receiver listens at;nettwork the transmitter sends to')
parser.add_argument('-port', metavar='port',default='None',help='Port TCP in case of 2 leaders')
parser.add_argument('-v', metavar='verbose', type=bool, default=False, help='Make the output verbose')

args = parser.parse_args()
node_info['device']=args.d
node_info['role']=args.role
node_info['BcastIP']=args.BcastIP
node_info['port']=args.port

#### TODO:Provisional: elimina el fichero de nodeID del Agent cada vez que se inicializa
if os.path.exists(_file_name):
    os.remove(_file_name)
############################################
# Reset globalDB by the LEADER
if node_info['role']== 'LEADER':
    requests.get('http://147.83.159.220:8000/reset_topoDB')
node_info['node_ID']=identificationProccess(node_info)
threadingSetup(node_info)
sleep(2)

if True: # TODO: Args ui activate
    th_ui()

# threadingJoining()