#!/usr/bin/python3
# dev module

#### Imports
import threading, socket
from time import sleep
from common import bcolors, custom_print, sendTo
from random import randrange


class RDIM:
    # TODO: Interrupt mode not implemented
    INTERRUPT = 0
    PULL = 1
    RESOURCE = 0
    SERVICE = 1
    OP_SETUP = 0
    OP_START = 1
    OP_STOP = 2
    PERM_R = 'r'
    PERM_W = 'w'
    PERM_RW = 'rw'
    PERM_RE = 're'
    PERM_WS = 'ws'
    PERM_RWS = 'rws'

    def __init__(self):
        self.resources_db = {}
        self.servicereq_db = {}
        self.lock_resources_db = threading.Lock()
        self.lock_servicereq_db = threading.Lock()

    def addResource(self, IDr, RES_type, RObject, Status):
        with self.lock_resources_db:
            self.resources_db[IDr] = [RES_type, RObject, Status]

    def addServiceRequest(self, IDs, Addr, RES_ID, Permissions, SObject, IntORPull):
        with self.lock_servicereq_db:
            self.servicereq_db[IDs] = [Addr, RES_ID, Permissions, SObject, IntORPull]

    def output_device(self, ID_RES, Status):
        # Output from device
        with self.lock_resources_db:
            r = self.resources_db.get(ID_RES)
            r[2] = Status
            self.resources_db[ID_RES] = r       #todo: This is correct or i'm crazy?

    def input_device(self, ID_RES, Status):
        # Input to device
        with self.lock_resources_db:
            r = self.resources_db.get(ID_RES)
            r[2] = Status
            r[1].recvAction(Status)
            self.resources_db[ID_RES] = r

    def put(self, ID_SER, Status):
        # From service to resource
        with self.lock_servicereq_db:
            r = self.servicereq_db.get(ID_SER)
            perm = r[2]
            if perm == self.PERM_W or perm == self.PERM_RW or perm == self.PERM_RWS or perm == self.PERM_WS:
                self.input_device(r[1],Status)

    def get(self, ID_SER):
        # Service gets status from resource (Stored value in RDIM)
        with self.lock_servicereq_db:
            r = self.servicereq_db.get(ID_SER)
            perm = r[2]
            if perm == self.PERM_R or perm == self.PERM_RW or perm == self.PERM_RE or perm == self.PERM_RWS:
                return self.resources_db.get(r[1])[2]

    def opperate_object(self, ID, OP_TYPE, ResORSer, callback=None):
        object = None
        if ResORSer == self.RESOURCE:
            with self.lock_resources_db:
                if ID in self.resources_db.keys():
                    r = self.resources_db.get(ID)
                    object = r[1]
        elif ResORSer == self.SERVICE:
            with self.lock_servicereq_db:
                if ID in self.servicereq_db.keys():
                    r = self.servicereq_db.get(ID)
                    object = r[3]
        if object is not None:
            if OP_TYPE == self.OP_SETUP:
                if self.SERVICE == ResORSer:
                    object.setup()
                elif self.RESOURCE == ResORSer:
                    object.setup(callback,ID)
            elif OP_TYPE == self.OP_START:
                object.start()
            elif OP_TYPE == self.OP_STOP:
                object.stop()

    def getResType(self, id_res):
        with self.lock_resources_db:
            if id_res in self.resources_db.keys():
                return self.resources_db[id_res][0]

    def getResID(self, id_ser):
        if id_ser in self.servicereq_db.keys():
            return self.servicereq_db[id_ser][1]

    def getResourceTypeList(self):
        l = list()
        with self.lock_resources_db:
            for x in self.resources_db.keys():
                l.append(self.resources_db[x][0])
            return l

    def getResAlloc(self, res_type):
        with self.lock_resources_db:
            r_list = [res for res in self.resources_db.keys() if self.resources_db.get(res)[0] == res_type]
            if len(r_list) > 0:
                return r_list[randrange(0,len(r_list))]
        return -1


class ServiceAttention:
    BUFF_SIZE = 4092
    RETRY_ATTEMPTS = 4
    WAITTIME_PULL = 5
    def __init__(self, rdim_status_cbk, rdim_pull_cbk, ser_num, res_type, addr):
        """

        :param rdim_cbk: Put callback
        :param ser_num: ID service created from dev.py
        :param addr: ('IP',port)
        """
        self.ser_num = ser_num
        self._rdim_status_send_callback = rdim_status_cbk
        self._rdim_status_pull_callback = rdim_pull_cbk
        self.thread_recv = None
        self.thread_pull = None
        self._connected = False
        self.correct_connect = False
        trynum = 0
        while not self.correct_connect and trynum < self.RETRY_ATTEMPTS:
            try:
                self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.clientSocket.connect(addr)
                self.correct_connect = True
            except ConnectionRefusedError:
                print('Error. Connection Refused')
            finally:
                trynum += 1
        if self.correct_connect:
            # Send type to the service
            try:
                self.clientSocket.send(str(res_type).encode())
            except Exception as ex:
                print('Connection closed in SerAtt an init time')
                print(ex)
                self.correct_connect = False

    def start(self):
        self._connected = self.correct_connect
        self.thread_recv = threading.Thread(target=self.th_recv_from_service,name='SerATT_'+str(self.ser_num),daemon=True)
        self.thread_pull = threading.Thread(target=self.th_pull,name='SerATT_'+str(self.ser_num)+'_pull',daemon=True)
        self.thread_recv.start()
        self.thread_pull.start()

    def setup(self):
        # Only as interface method - Does nothing as service, only for devices
        pass

    def stop(self):
        self._connected = False
        if self.clientSocket is not None:
            self.clientSocket.close()

    def th_recv_from_service(self):
        while _connected:
            msg = (self.clientSocket.recvfrom(self.BUFF_SIZE))[0].decode('utf-8')
            if msg != '':
                self._rdim_status_send_callback(self.ser_num,msg)

    def th_pull(self):
        while _connected:
            self.sendStatus(self._rdim_status_pull_callback(self.ser_num))
            sleep(self.WAITTIME_PULL)

    def send_to_service(self, status):
        if _connected:
            self.clientSocket.send(str(status).encode())

    def sendStatus(self, status):
        self.send_to_service(status)


#### Private variables
__setup_done__ = False
cp = None
_tag = bcolors.HEADER+'DV'+bcolors.ENDC
_ip_cbk = None

#### Global variables
_connected = False
_gpio = None
_rdim = RDIM()
_idr = 0
_ids = 0
_lock_ids = threading.Lock()


thread_module = None
thread_recv = None
thread_send = None
thread_proc = None


###############################################
#                   Threads
###############################################

def th_module(): # TODO: Maybe we don't need anymore this thread
    global _connected
    # 1. Start all the resources/services added in setup time
    with _rdim.lock_resources_db:
        resources = list(_rdim.resources_db.keys())
    for resource in resources:
        _rdim.opperate_object(resource, _rdim.OP_START, _rdim.RESOURCE)
    with _rdim.lock_servicereq_db:
        services = list(_rdim.servicereq_db.keys())
    for service in services:
        _rdim.opperate_object(service,_rdim.OP_START, _rdim.SERVICE)

    # 3. Wait loop
    while _connected:
        sleep(0.1)

    # 4. Gracefull resource/serviceatt stop
    with _rdim.lock_servicereq_db:
        services = list(_rdim.servicereq_db.keys())
    for service in services:
        _rdim.opperate_object(service,_rdim.OP_STOP, _rdim.SERVICE)
    with _rdim.lock_resources_db:
        resources = list(_rdim.resources_db.keys())
    for resource in resources:
        _rdim.opperate_object(resource, _rdim.OP_STOP, _rdim.RESOURCE)


###############################################
#                   Functions
###############################################


###############################################
#                   Interface
###############################################

def request_resource(res_type, addr):
    global _ids
    if res_type in _rdim.getResourceTypeList():
        res_id = _rdim.getResAlloc(res_type)
        with _lock_ids:
            sobj = ServiceAttention(_rdim.put,_rdim.get,_ids,res_type,addr)
            _rdim.addServiceRequest(_ids, addr, res_id, _rdim.PERM_RWS, sobj, _rdim.PULL)
            _rdim.opperate_object(_ids, _rdim.OP_START, _rdim.SERVICE)
            _ids += 1


def setup(type, gpio, ip_cbk=None, verbose=False):
    global _gpio, __setup_done__, cp, _ip_cbk, _idr, _ids
    _gpio = gpio
    _ip_cbk = ip_cbk
    cp = custom_print(verbose,_tag)

    # TODO: Here put more types!
    # Type discrimination. Import all the devices needed
    if str(type).lower() == 'sem':
        import device_sem as devi
        resource_type = 'SEM'
    elif str(type).lower() == 'car':
        import device_car as devi
        resource_type = 'CAR'
    elif str(type).lower() == 'amb':
        import device_car as devi
        resource_type = 'AMB'
    elif str(type).lower() == 'bom':
        import device_car as devi
        resource_type = 'BOM'
    elif str(type).lower() == 'bfr':
        import device_building_fire as devi
        resource_type = 'TEMP'
    else:
        devi = None
        resource_type = ''

    # TODO: setupRDIM: More Devices and services
    if devi is not None:
        _rdim.addResource(_idr,resource_type,devi,'')
        _idr += 1

    # Setup all the services/resources
    for resource_id in _rdim.resources_db.keys():
        _rdim.opperate_object(resource_id,_rdim.OP_SETUP,_rdim.RESOURCE,callback=_rdim.output_device)
    for service_id in _rdim.resources_db.keys():
        _rdim.opperate_object(service_id,_rdim.OP_SETUP,_rdim.RESOURCE,callback=_rdim.output_device)

    __setup_done__ = True


def start():
    global _connected, thread_module
    if not __setup_done__:
        setup('', False)
    _connected = True

    cp.vprint('Module started')
    thread_module = threading.Thread(target=th_module,daemon=True)
    thread_module.start()


def stop():
    global _connected, thread_module
    _connected = False
    if thread_module is not None:
        thread_module.join()
    if cp is not None:
        cp.vprint('Module stoped')
