from pymongo import MongoClient
import json
import os
import threading
from time import sleep

from bson import json_util
from pymongo import MongoClient

service = {
    'serv_id':'None',
    'code': 'None',
    'resources': 'None',
    'iot':'None',
    'output':'None',
    'priotity':'None',
    'dependencies':'None',

}

connected = True
def th_ui():
    global connected
    while connected:
        msg = input('->')
        if str(msg).lower() == 'exit':
            connected = False

# la mongoDB is running in cluster Zephyrus
#client=MongoClient('10.0.0.48', 27017)
client = MongoClient("mongodb://superAdmin:pass1234@10.0.0.48:27017/blog?ssl=false&authSource=admin")
# DBs definition
topoDB=client.globalDB #global database
nodes= {
    "address": "147.83.159.100",
    "role": "agent",
    "device":"on",
    "nodeID": 1234,

}
mesg= input('SERVICE/NODES?(s/n):')
th = threading.Thread(target=th_ui, daemon=True)
th.start()
#colections
collection=topoDB.nodes
catalog=topoDB.services
while connected:
    agent_list = []
    servlist= []
    sleep(5)
    os.system("clear")
    if mesg == 'n':
        num = collection.count_documents({})
        print("num:",num)
        for agent_mongo in collection.find():
            # convert mongo document to json
            agent_list.append(agent_mongo)
        agent_json = json.dumps(agent_list, default=json_util.default)
        for elem in agent_list:
            del elem['_id']
            print(elem)
    elif mesg =='s':
        for serv_mongo in catalog.find():
            servlist.append(serv_mongo)
        serv_json = json.dumps(servlist, default=json_util.default)
        for elem in servlist:
            del elem['_id']
            print(elem)
    else:
        print('Please, select SERVICE or NODES')
        mesg = input('SERVICE/NODES?(s/n):')