#!/usr/bin/python3.7
"""
#Attend request service
        - Check serv ID
        - Search serv in Catalog DB
        - Obtain serv requirements
        Return: requirements list

#Prepare Service
    - find service code
    - find involved agents acording to resources, IoT, ..
    Return: involved agents list, exec code


#Create Cluster
#Send to RunTime
"""
from printcolors import prt
import requests
import json
import RTMv2 as rtm
import pymysql
import os
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

service = {
    'serv_id':'None',
    'code': 'None',
    'resources': 'None',
    'iot':'None',
    'output':'None',
    'priotity':'None',
    'dependencies':'None',

}

############################################################################
#
#                       CLASSES
#
############################################################################

# class ldb : mysql DDBB to regidter node info
class ldb:
    cursor=None
    db=None

    """def __init__(self, inode):
       self.node_info = inode"""
    def conect(self):
        user=os.environ["USER"]
        self.db = pymysql.connect("localhost",user,"miau","LOCALDB" )

        # prepare a cursor object using cursor() method
        self.cursor = self.db.cursor()
    def reset(self):
        # Drop table if it already exist using execute() method.
        self.cursor.execute("DROP TABLE IF EXISTS info")

        # Create table as per requirement
        sql = """CREATE TABLE info (
         features  VARCHAR(500))"""
        try:
            # Execute the SQL command
            self.cursor.execute(sql)
            # Commit your changes in the database
            self.db.commit()
        except:
            # Rollback in case there is any error
            print("Error to create table in local DB")
            self.db.rollback()

    def update(self,node_info):

        sql = "INSERT INTO `info`(features) VALUES (%s)"

        try:
            # Execute the SQL command
            self.cursor.execute(sql,json.dumps(node_info))
            # Commit your changes in the database
            self.db.commit()
        except:
            # Rollback in case there is any error
            self.db.rollback()

    def get(self):
        # read tables
        self.cursor.execute(" select * from info")
        for fila in self.cursor:
            fila=json.loads(fila[0])
        return fila


    def close(self):
        # disconnect from server
        self.db.close()

printing=prt()


####################################################################
#                   INTERFACE
####################################################################
class SEXiface:
    def callsexAgent(self,selec):
        ServID2SEXAgent(selec)
    def callcheckServ(self,serv_req):
        CheckServID(serv_req)

####################################################################
#                   INTERFACE FUNCTIONS
####################################################################
def ServID2SEXAgent(selec):

    # check localDB to obtain node_info -> myIP
    localDB = ldb()
    localDB.conect()
    node_info = localDB.get()
    localDB.close()
    #Agent request service to API Agent
    API_addr_get = 'http://' + node_info['myIP'] + ':8000/sexAgent2APIAgent'
    #PARAMS = "selec='serv_id':"+"'"+selec['serv_id']+"','leaderIP':"+"'"+node_info['leaderIP']+"'"
    PARAMS = str("selec="+selec['serv_id']+","+node_info['leaderIP']+","+node_info['myIP'])
    response = requests.get(API_addr_get, PARAMS).json()
#Check serv ID
def CheckServID(serv_req):
    parameters=None
    try:
        # check localDB to obtain node_info -> myIP
        ckeckDB = ldb()
        ckeckDB.conect()
        node_info = ckeckDB.get()
        print("node_info", node_info)
        print("ser_req:",serv_req)
        if serv_req != None:
            PARAMS = "selec={'serv_id':" + "'" + serv_req[0] + "'}"
            API_addr_get = 'http://' + node_info['myIP'] + ':8000/get_servDB'
            response = (requests.get(API_addr_get, PARAMS)).json()
            if response == "[]":
                printing.error("SERVICE NOT EXIST")
            else:
                response = json.loads(response)
                parameters=AttendServ(response)
    except Exception as ex:
        text = str("Err in CheckServID: "+str(ex))
        printing.error(text)
    ckeckDB.close()
    return parameters
########################################################################
#                   SERVICE ATTENTION
########################################################################

def AttendServ(serv_info):
    # check localDB to obtain node_info -> myIP
    ckeckDB = ldb()
    ckeckDB.conect()
    node_info = ckeckDB.get()
    parameters= []
    serv_info=serv_info[0]
    del serv_info['_id']
    text = str("Service  "+serv_info['serv_id']+" ATTENDED:")
    printing.service(text)
    node_exec = node_info['myIP']
    # Resolve Dependencies
    if serv_info['dependencies'] != 'None':
        print(serv_info['dependencies'])
        depenlist= serv_info['dependencies'].split(",")
        print(depenlist)
        for servDep in depenlist:
            text = str("Resolving Dependency-check ServID & AttendServ: " + servDep)
            printing.service(text)
            out=CheckServID((servDep,))
            parameters.append(out)
            print("parameters return from CheckServID:",parameters)
    # obtain Agent IP with required Iot
    if serv_info['iot'] != 'None':
        text = str("obtain Agent IP with required Iot... ")
        printing.service(text)
        PARAMS = "selec={'IoT':" + "'" + serv_info['iot'] + "'}"
        API_addr_get = 'http://' + node_info['leaderIP'] + ':8000/get_topoDB'
        response = (requests.get(API_addr_get, PARAMS)).json()
        node_exec = json.loads(response[0])[0]
        print("Agent IP:",node_exec['myIP'])
    # if no iot codexec is executed in "location" (leader, agent ,cloud)
    else:
        text = str("obtain Agent IP with required Location... ")
        printing.service(text)
        PARAMS = "selec={'role':" + "'" + serv_info['location'] + "'}"
        API_addr_get = 'http://' + node_info['leaderIP'] + ':8000/get_topoDB'
        response = (requests.get(API_addr_get, PARAMS)).json()
        node_exec = json.loads(response[0])[0]
        print("Node to exec IP:", node_exec['myIP'])

#TODO: Revision from here

    ##### Call Run Time Module  ##########
    # add agent IP to service
    serv_info['agent']=node_exec['myIP']
    # post dependencies results in "'params':" key
    serv_info['params']= parameters
    out=callRunTime(serv_info)
    text=str("parameters return form CallRunTime:")
    printing.service(text)
    print(out)
    #parameters=json.loads(parameters)
    if out==None:
        printing.service("Service exec SUCCESSFULLY")

    return out

def getExeCode(source):
    printing.service('Get exec Code from source')
    printing.service(source)

def code2exeNode(exenode):
    printing.service('sending exec Code to Exec Node')

def setupCluster(parameters):
    exeNode = None
    # Select exeNode
    printing.service('Selecting Exec Node')
    # create TCP connextion btwn exeNode and rest nodes
    printing.service('Creating Cluster')
    return json.dumps(exeNode)

def callRunTime(serv_info):
    # check localDB to obtain node_info -> myIP
    ckeckDB = ldb()
    ckeckDB.conect()
    node_info = ckeckDB.get()
    printing.service('Call Node Run Time Module')
    API_addr_get = 'http://' + serv_info['agent'] + ':8000/callRT'
    #PARAMS = str("selec="+'parameters')
    response = requests.post(API_addr_get,data=serv_info).json()
    text=str('RunTime result:')
    printing.service(text)
    print(response)
    # return parameterss if necessary. Check output key
    if serv_info['output']=='False':
        response = None
    return response

#########  MAIN  ################

if __name__ == "__main__":
    printing=prt()
    printing.warning('hola')
    printing.succful('hola')
    printing.error('hola')
    printing.service('hola')
    print('adeu')