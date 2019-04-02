import hug
import pprint
import json
from bson.json_util import dumps
from bson import json_util

from pymongo import MongoClient

# la mongoDB is running in cluster Zephyrus
client=MongoClient('10.0.0.27', 27017)

topoDB=client.globalDB
nodes= {
    "address": "147.83.159.100",
    "role": "agent",
    "device":"on",
    "nodeID": 1234,

}
#Method.
collection=topoDB.nodes

@hug.post('/post_topoDB')
def post_topoDB(body):
    """Insert a new document
    Request:response=(requests.post('http://147.83.159.220:8000/post_topoDB', data=post)
    being
    node_info={
        'device':'None',
        'role':'None',
        'myIP':'None',
        'leaderIP':'None',
        'port':'None',
        'node_ID':'None',
        'IoT':'None'
    }"""
    print(body,type(body))

    post_id = collection.insert_one(body).inserted_id

@hug.post('/update_topoDB')

def update_topoDB(body):
    """Update database if data exists, else post a new document
    Request:response=(requests.post('http://147.83.159.220:8000/update_topoDB', data=node_info))"""

    print("dic:",body,"type:", type(body))
    collection.update({'myIP':body['myIP']},{"$set":body},True)

@hug.get('/get_topoDB')
def get_topoDB(selec=None):
    """
    PARAMS="selec={'myIP':"+"'"+node_info['myIP']+"'}"
    request:response=(requests.get('http://147.83.159.220:8000/get_topoDB',PARAMS)).json() """
    agent_list=[]
    if selec != None:
        selec=eval(selec)
        print(selec,type(selec))
    num = collection.count_documents({})
    for agent_mongo in collection.find(selec):
    # convert mongo document to json
        print("type agentmongo:", type(agent_mongo))
        agent_list.append(agent_mongo)

    agent_json = json.dumps(agent_list, default=json_util.default)
    print(agent_json)
    #selec = json.dumps(selec, default=json_util.default)
    return agent_json, num, selec

@hug.get('/del_topoDB')
def del_topoDB(index=None):
    """request: requests.get('http://147.83.159.220:8000/del_topoDB',"index={'rol': 'leader'}")"""
    index=eval(index)
    print(index, type(index))
    collection.delete_many(index)
# reset all documents
@hug.get('/reset_topoDB')
def reset_topoDB():
    """request: requests.get('http://147.83.159.220:8000/reset_topoDB')"""
    collection.remove({})
