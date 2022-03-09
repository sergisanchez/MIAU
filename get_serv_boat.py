import hug
import requests
import json
import webbrowser
import subprocess,sys,os


##Dades login
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

@hug.get('/get_execode')
def get_execode(URL_code=None):
    token = post_serv_token()
    request= requests.get(URL_code,headers={'access-token': token})
    return request

if __name__ == "__main__":
    serv_in= input("Service Request Name:")
    serv_in=serv_in.split(" ")
    serv_name=serv_in[0]
    if len(serv_in)>1:
        param=serv_in[1]
    token=post_serv_token()
    print(token)
    serv_answ=boat_get_serv(serv_name)
    if serv_answ:
        resp = json.loads(serv_answ.text)
        print(resp)
        if 'pi' not in resp[0][serv_name]['dependencies']:
            print("no existen dependencias")
        else:
            print("dependencias")
            serv_answ = boat_get_serv(resp[0][serv_name]['dependencies'])
            resp = json.loads(serv_answ.text)
            print(resp)

    ## Es una web?

    try:
        filexec=open('codexec.py',mode='w')
        execode=get_execode(resp[0][serv_name]['code'])
        #print(execode.content.decode('UTF-8'))
        for line in execode.content.decode():
            filexec.write(line)
        #result=exec(execode.content)
        #out = subprocess.check_output(['python3','codexec.py'], universal_newlines=True,input=b'10')
        process = subprocess.run(['python3','out.py'], input='10',capture_output=True,check=True, universal_newlines=True)
        output = process.stdout
        print("output", output.splitlines ())
        #os.environ['PYTHONUNBUFFERED'] = "1"
        #process = subprocess.run([sys.executable,'codexec.py'],input='10',stderr=subprocess.PIPE,stdout=subprocess.PIPE,universal_newlines=True)
        #print("proces: ",process)

    except Exception as ex:
        print(ex)
