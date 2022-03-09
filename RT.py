from printcolors import prt
import subprocess,os
import requests
import json
import pysftp
import pymysql
import threading
from SEX import ldb
printing=prt()

# Access Repository ###############
myHostname = "10.0.0.48"
myUsername = "root"
remotePath = "/root/MIAU_devlpmt/pyServices/"
localFilePath = "./execode.py"
####################################################################
#                   INTERFACE
####################################################################
class RTiface:
    def callRTAgent(self,params):
        result = attendRT(params)
        return result

####################################################################
#                 FUNCTIONS
####################################################################

def attendRT(serv_info):
    text = str('get code...')
    printing.runtime(text)
    get_execode(serv_info)
    try:
        text = 'Running code...'
        printing.runtime(text)
        input_data='None'
        if serv_info['input'] == 'True':
            input_data=json.dumps(serv_info['params'])
        result= subprocess.check_output('python3 execode.py',input=input_data, shell=True, universal_newlines=True)
        print("result: ", result)

    except Exception as ex:
        printing.error(ex)
    return result


def get_execode(body):
    print("selec:",body)
    remoteFilePath = remotePath + body['code']
    with pysftp.Connection(host=myHostname, username=myUsername) as sftp:
        text = 'Repo Connection succesfully stablished ...'
        printing.runtime(text)
        sftp.get(remoteFilePath,localFilePath)


