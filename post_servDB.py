from pymongo import MongoClient
service = {
    'serv_id':'None',
    'code': 'None',
    'input': 'None',
    'output': 'None',
    'resources': 'None',
    'iot':'None',
    'location' :'None',
    'agentlist':'None',
    'priotity':'None',
    'dependencies':'None',

}
# la mongoDB is running in cluster Zephyrus
#client=MongoClient('10.0.0.27', 27017)
client = MongoClient('mongodb://superAdmin:pass1234@10.0.0.48:27017/blog?ssl=false&authSource=admin')
# DBs definition
topoDB=client.globalDB #global database
catalog=topoDB.services
def inputServ():
    global catalog,service
    print("Enter Service description")
    print('current data: enter new data')
    cdata=str('serv ID : ')
    msg=input(cdata)
    getserv={}

    for getserv in catalog.find({'serv_id':msg}):
        print("getserv: ",getserv)
        service=getserv
        print("Update service:")
    if getserv =={}:
        print("Enter New service")
        cdata = str('(serv_id = ' + service['serv_id'] + ')' + ':')
        msg = input(cdata)

    if msg !='':
        service['serv_id']=msg

    cdata = str('(code = ' + service['code'] +')'+ ': (introduce url follows of comma (,)')
    msg = input(cdata)
    if msg != '':
        # open source file and add to dicctionary. If source file is greater than 16MB, use GridFS
        #(https: // docs.mongodb.com / manual / core / gridfs /)
        #f = open(msg)
        #msg=f.readlines()
        msg=msg.split(",")
        service['code'] = msg[0]
        #f.close()

    cdata = str('(input (False/True) = ' + service['input'] + ')' + ':')
    msg = input(cdata)
    if msg != '':
        service['input'] = msg

    cdata = str('(output (False/True) = ' + service['output'] + ')' + ':')
    msg = input(cdata)
    if msg != '':
        service['output'] = msg

    cdata = str('(Resources = ' + service['resources'] +')'+ ':')
    msg = input(cdata)
    if msg != '':
        service['resources'] = msg

    cdata = str('(iot = ' + service['iot'] +')'+ ':')
    msg = input(cdata)
    if msg != '':
        service['iot'] = msg

    cdata = str('(location (CLOUD,LEADER,AGENT) = ' + service['location'] + ')' + ':')
    msg = input(cdata)
    if msg != '':
        service['location'] = msg

    cdata = str('(Agentlist = ' + service['agentlist'] +')'+ ':')
    msg = input(cdata)
    if msg != '':
        service['agentlist'] = msg

    cdata = str('(priority = ' + service['priotity'] +')'+ ':')
    msg = input(cdata)
    if msg != '':
        service['priotity'] = msg

    cdata = str('(Dependencies = ' + service['dependencies'] + ')'+':')
    msg = input(cdata)
    if msg != '':
        service['dependencies'] = msg
    print(service)

def updateServDB(body):
    catalog.update_one({'serv_id':body['serv_id']},{"$set":body},True)

def deleteServ(index):
    index={'serv_id':index}
    #index=eval(index)
    catalog.delete_many(index)

def modifyServDB(service):
    print("Enter Service to modify")
    cdata = str('serv ID : ')
    msg = input(cdata)
    getserv = {}

    for getserv in catalog.find({'serv_id': msg}):
        print("getserv: ", getserv)
        service = getserv
        print("Update service:", service['serv_id'])
    msg=input("add/del key? (a/d) : ")
    if msg == 'a':
        key= input("intro key:")
        value=input("intro value: ")
        service[key]=value
    elif msg == 'd':
        key = input("intro delete key:")
        del service[key]
    return service

if __name__ == "__main__":
    msg=input('SERVICE: INSERT(update)/DELETE (serv)/MODIFY(key)? (i/d/m) :')
    if msg =='i':
        inputServ()
        updateServDB(service)
    elif msg =='d':
        msg=input('serv_id?: ')
        deleteServ(msg)
    elif msg == 'm':
        service= modifyServDB(service)
        updateServDB(service)