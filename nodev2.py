#!/usr/bin/python3.8
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
import os, argparse, subprocess
import threading
from time import sleep
import requests
import RTMv2 as rtm
from common import custom_print
cstp = custom_print(True,'[node.py] ')

def nop():
    pass

#### PID
print('PID: ' + str(os.getpid()))

######
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
    'portUDP':'None',
    'portTCP':'None',
    'BcastIP':'None',
    'node_ID':'None',
    'IoT':'None'
}

###############################################
#                   Threads
###############################################

def th_RTM(node_info):

    node_info=rtm.setup(node_info, verbose=True, ip_cbk=ipValue)
    node_info['myIP']=rtm.getmyIP(node_info)
    connected=rtm.start(node_info)

    while connected:
        nop()

    rtm.stop()


def th_ui(pid):
    global connected
    while connected:
        msg = input('->')
        if str(msg).lower() == 'exit':
            connected = False
            pid.kill()
            print("hug ", pid.pid," closed")

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


def identificationProccess():
    import random
    nodeID = str(random.randint(0, 100000000))
    return nodeID


###############################################
#                   AGENT in Thread
###############################################

# Args

parser.add_argument('d', metavar='device', default='NONE', help='device: CAR/SEM/AMB/BOM/BUI_F/BUI_I/BUI_J')
parser.add_argument('role', choices={'LEADER': 'LEADER', 'AGENT': 'AGENT'}, help='which role to take')
parser.add_argument('-g', metavar='gpio', type=bool, default=False, help='GPIO enabled')
parser.add_argument('-B', metavar='BcastIP',default=None,help='interface the receiver listens at;nettwork the transmitter sends to')
parser.add_argument('-portUDP', metavar='portUDP',default='None',help='Port UDP')
parser.add_argument('-portTCP', metavar='portTCP',default='None',help='Port TCP in case of 2 leaders')
parser.add_argument('-v', metavar='verbose', type=bool, default=False, help='Make the output verbose')

args = parser.parse_args()
node_info['device']=args.d
node_info['role']=args.role
node_info['BcastIP']=args.B
node_info['portUDP']=args.portUDP
node_info['portTCP']=args.portTCP
node_info=rtm.IoTset(node_info)


############################################


if node_info['role']== 'LEADER':
    if node_info['BcastIP'] == None:
        node_info['BcastIP']=rtm.get_bcastaddr()
    node_info['myIP']=rtm.getmyIP(node_info)
    node_info['leaderIP']=node_info['myIP']
    # starting API REST

    API_addr_get = 'http://' + node_info['myIP'] + ':8000/get_topoDB'
    try:
        requests.get(API_addr_get)
        print("API is Running")

    except Exception as ex:
        print("*********** Start API ******")
        pid=subprocess.Popen(["hug", "-f", "API_node.py","&"], stdout=True)
        # Reset globalDB by the LEADER
        sleep(5)
        API_addr_reset = 'http://' + node_info['myIP'] + ':8000/reset_topoDB'
        # requests.get('http://147.83.159.220:8000/reset_topoDB')
        requests.get(API_addr_reset)
        # Register info LEADER in globalDB

        API_addr_update = 'http://' + node_info['myIP'] + ':8000/update_topoDB'
        response = (requests.post(API_addr_update, data=node_info))


elif node_info['role']== 'AGENT':
    if node_info['BcastIP'] == None:
        node_info['BcastIP']=rtm.get_bcastaddr()
    node_info['myIP']=rtm.getmyIP(node_info)
    node_info['BcastIP']=""
    # starting API REST in AGENT

    API_addr_get = 'http://' + node_info['myIP'] + ':8000/get_topoDB'
    try:
        requests.get(API_addr_get)
        print("API is Running")

    except Exception as ex:
        print("*********** Start API ******")
        pid=subprocess.Popen(["hug", "-f", "API_node.py","&"], stdout=True)



node_info['node_ID']=identificationProccess()

threadingSetup(node_info)
sleep(2)

if True: # TODO: Args ui activate
    th_ui(pid)

