import hug
import json
from bson import json_util
import requests
from pymongo import MongoClient
from SEX import SEXiface
from RT import RTiface
from printcolors import prt
import threading

printing=prt()
# la mongoDB is running in cluster Zephyrus
#client=MongoClient('10.0.0.48',27017, connect=False)
client = MongoClient('mongodb://superAdmin:pass1234@10.0.0.48:27017/blog?ssl=false&authSource=admin')
# DBs definition
topoDB=client.globalDB #global database
nodes= {
    "address": "147.83.159.100",
    "role": "agent",
    "device":"on",
    "nodeID": 1234,

}
service = {
    'serv_id':'None',
    'code': 'None',
    'resources': 'None',
    'iot':'None',
    'output':'None',
    'priotity':'None',
    'dependencies':'None',

}
# Access Boat Services dates ###############

user = 'test'
passwd = 'tset'
app = 'gW6l4cq1bwCSwQ'
URL_login = 'http://craaxcloud.epsevg.upc.edu:39000/login'
URL_help = 'http://craaxcloud.epsevg.upc.edu:39000/help'
URL_services_list = 'http://craaxcloud.epsevg.upc.edu:39000/services'
URL_services = 'http://craaxcloud.epsevg.upc.edu:39000/service'
## JSON login
datalogin = {
    "user": user,
    "password": passwd,
}

#colections #############################################
coleccio=topoDB.nodes
catalog= topoDB.services


###########################################################################
#
#                               RTM functions
#
###########################################################################


@hug.post('/post_topoDB')
def post_topoDB(body):
    """Description: Insert a new document
    Input:node_info={
        'device':'None',
        'role':'None',
        'myIP':'None',
        'leaderIP':'None',
        'port':'None',
        'node_ID':'None',
        'IoT':'None'
}
    Output: none
    Request:response=(requests.post('http://147.83.159.220:8000/post_topoDB', data=node_info))

    }"""
    #print(body,type(body))

    post_id = coleccio.insert_one(body).inserted_id

@hug.post('/update_topoDB')

def update_topoDB(body):
    """Descripcion: Update database if data exists, else post a new document
    Input:node_info={
        'device':'None',
        'role':'None',
        'myIP':'None',
        'leaderIP':'None',
        'port':'None',
        'node_ID':'None',
        'IoT':'None'
        }
    Output: none
    Request:response=(requests.post('http://147.83.159.220:8000/update_topoDB', data=node_info))"""

    #print("dic:",body,"type:", type(body))
    coleccio.update({'myIP':body['myIP']},{"$set":body},True)

@hug.get('/get_topoDB')
def get_topoDB(selec=None):
    """Description: get agent info form topoDB
    input: PARAMS="selec={'myIP':"+"'"+node_info['myIP']+"'}"
    output: agent_json: json with info agent:{'device':'None','role':'None','myIP':'None','leaderIP':'None','port':'None','node_ID':'None','IoT':'None'}
    request:response=(requests.get('http://147.83.159.220:8000/get_topoDB',PARAMS)).json() """
    try:
        agent_list=[]
        if selec != None:
            selec=eval(selec)
            #print(selec,type(selec))
        num = coleccio.count()
        #num=5
        text="num:"+str(num)
        printing.api(text)
        for agent_mongo in coleccio.find(selec):
        # convert mongo document to json
            #print("type agentmongo:", type(agent_mongo))
            agent_list.append(agent_mongo)

        agent_json = json.dumps(agent_list, default=json_util.default)
        #print(agent_json)
        #selec = json.dumps(selec, default=json_util.default)
    except Exception as ex:
        text="Error on get TopoDB"
        printing.api(text)
        print(ex)
    return agent_json,num, selec

@hug.get('/del_topoDB')

def del_topoDB(index=None):
    """Description: remove agent info form topoDB
    input: PARAMS = "index={'myIP':" + "'" + addr[0] + "'}"
    output:none
    request:response=(requests.get(''http://' + node_info['leaderIP'] + ':8000/del_topoDB',PARAMS)).json()
"""
    index=eval(index)
    #print(index, type(index))
    coleccio.delete_many(index)
# reset all documents
@hug.get('/reset_topoDB')
def reset_topoDB():
    """Description: remove all topoDB elements
    Input: none
    Output: none
    request: requests.get('http://147.83.159.220:8000/reset_topoDB')"""
    coleccio.remove({})


###########################################################################
#
#                               SEX fuctions
#
###########################################################################


@hug.post('/servID2leader')

def servID2leader(body):
    """Description: function not in use
    Input: none
    Output: none
    request: requests.get('http://147.83.159.220:8000/reset_topoDB')"""

    API_addr_post = 'http://' + body['leaderIP'] + ':8000/servIDfromAgent'
    response= requests.post(API_addr_post, data=body)



@hug.get('/req2APIAgent')

def req2APIAgent(selec):
    """Description: API AGENT recv Service request from user. Send to SEX Agent
        Input: PARAMS="selec={'serv_id':"+"'"+service['serv_id']+"'}"
        Output: None
         CALL: SEX.ServID2SEXAgent
        request: requests.get('http://' + node_info['myIP'] + ':8000/req2APIAgent',PARAMS').json()"""
    iface=SEXiface()
    selec=eval(selec)
    text="API AGENT recv Service request. Send to SEX Agent"
    printing.api(text)

    run = threading.Thread(name="ServID to SEX AGENT", target=iface.callsexAgent, args=(selec,), daemon=True)
    run.start()


@hug.get('/sexAgent2APIAgent')

def sexagent2APIAgent(selec):
    """Description: API AGENT recv Service request from SEX AGENT. Send to API LEADER.
            Input: PARAMS = str("selec="+<service_name>+","+node_info['leaderIP'])
            Output: None
             CALL: attenServID2APILeader
            request: requests.get('http://' + node_info['myIP'] + ':8000/sexAgent2APIAgent',PARAMS').json()"""

    try:
        if type(selec)==type("hi"):
            selec=selec.split(",")
        if selec[1] == selec[2]:
            text = "LEADER recv Service request.LEADER attend service. " + str(selec)
            printing.api(text)
            attenServID2APILeader(selec[0])
        else:
            text="API AGENT recv Service request from SEX AGENT. Send to API LEADER. "+str(selec)
            printing.api(text)
            API_addr_get = 'http://' +selec[1]+ ':8000/attenServID2APILeader'
            PARAMS = str("selec="+selec[0]+',')
            response = requests.get(API_addr_get, PARAMS).json()
            printing.api("sending to API Leader...")
    except Exception as ex:
        printing.error(ex)


@hug.get('/attenServID2APILeader')

def attenServID2APILeader(selec):
    """Description: API Leader recv from API AGENT derv request. Send to SEX leader
        Input: PARAMS = str("selec="+<service_name>+',')
        Output: None
        CALL: SEX.CheckServID
        request: requests.get('http://' +selec[1]+ ':8000/attenServID2APILeader',PARAMS').json()"""

    try:
        try:
            selec=selec.split(',')
        except Exception as ex:
            pass
        text="API Leader recv from API AGENT:"+str(selec)+". Send to SEX leader"
        printing.api(text)
        iface = SEXiface()
        #selec = eval(selec)
        run = threading.Thread(name="to SEX Leader", target=iface.callcheckServ, args=(selec,), daemon=True)
        run.start()
    except Exception as ex:
        text="Error in Leader reception!!!"
        printing.error(ex)


@hug.post('/update_servDB')

def update_servDB(body):
    """Description:Update database if data exists, else post a new document
    Request:response=(requests.post('http://147.83.159.220:8000/update_servDB', data=node_info))"""
    #print("serv:",body,"type:", type(body))
    catalog.update({'serv_id':body['serv_id']},{"$set":body},True)


@hug.get('/get_servDB')
def get_servDB(selec=None):
    """Description: get service info from servDB
    Input: PARAMS = "selec={'serv_id':" + "'" + <service_name> + "'}"
    Output: service = {'serv_id':'None','code': 'None','resources': 'None','iot':'None','output':'None','priotity':'None','dependencies':'None',}
    request:response=(requests.get('http://147.83.159.220:8000/get_servDB',PARAMS)).json() """
    try:
        agent_list=[]

        if selec != None:
            selec=eval(selec)
        #num = catalog.count()
        for agent_mongo in catalog.find(selec):
            agent_list.append(agent_mongo)

        agent_json = json.dumps(agent_list, default=json_util.default)
        #print("get ServDB:",agent_json)

    except Exception as ex:
        printing.error(ex)
    return agent_json

@hug.get('/del_servDB')
def del_servDB(index=None):
    """request: requests.get('http://147.83.159.220:8000/del_servDB',"index={'serv_id': 'emerg'}")"""
    index=eval(index)
    #print(index, type(index))
    catalog.delete_many(index)
# reset all documents
@hug.get('/reset_servDB')
def reset_servDB():
    """request: requests.get('http://147.83.159.220:8000/reset_servDB')"""
    catalog.remove({})

####### Service Request to Boat Database  ####################
## Doumentation: /home/sergi/Escritorio/CRAAX/testbed/boat Service/bAPI.pdf

@hug.get('/boat_get_serv')
def post_serv_token():


    ## Petició login
    try:
        request = requests.post(URL_login, json=datalogin)
        if request:
            data = json.loads(request.text)
            token = data["token"]
            return(token)
        else:
            exit()
    except Exception as ex:
        print(ex)


def boat_get_serv(serv_name):

    try:
        token = post_serv_token()
        request=requests.get(URL_services,headers={'access-token': token}, json={"key":serv_name})
        return request
    except Exception as ex:
        print(ex)




###########################################################################
#
#                               RT fuctions
#
###########################################################################
@hug.post('/get_execode')
def get_execode(body):
    print("selec:",body)
    if body != None:
        body = eval(body)
        text='selec[code]:'+body['code']
        printing.api(text)
    token = post_serv_token()
    request= requests.get(body['code'],headers={'access-token': token})
    return request


@hug.post('/callRT')
def callRT(body):
    iface=RTiface()
    text=str('Attend RT request...'+body['agent'])
    printing.api(text)
    print("body:", body)
    results=iface.callRTAgent(body)
    return results

@hug.get('/checkIoT2APIagent')
def checkIoT2APIagent(agentIP,IoTtype,data=None):
    pass

def checkIoT2RTagent():
    """RT interface"""
    pass
@hug.get('/actIoT2APIagent')
def actIoT2APIagent(agentIP,IoTtype,data=None):
    pass

def actIoT2RTagent():
    """RT interface"""
    pass