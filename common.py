import sys, socket


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[34m'
    OKGREEN = '\033[32m'
    OKGREENH = OKGREEN+'['
    WARNING = '\033[33m'
    WARNINGH = WARNING + '['
    FAIL = '\033[31m'
    FAILH = FAIL + '['
    ENDC = '\033[0m'
    ENDCH = ']: ' + ENDC
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ERROR = FAILH + 'ERROR' + ENDCH
    '''
    To use this code, you can do something like
    print bcolors.WARNING + "Warning: No active frommets remain. Continue?" + bcolors.ENDC
    '''


class custom_print:
    def __init__(self, verbose=False, tag=''):
        self._verbose = verbose
        self._tag = tag

    def vprint(self, *args, **kwargs):
        if self._verbose:
            if self._tag != '':
                print(self._tag,*args,**kwargs)
            else:
                print(*args,**kwargs)

    def eprint(self, *args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)


def sendTo(addr_dest, msg='', proto='TCP', reply=False, replyCallback=None):
    if not type(addr_dest) is list and not type(addr_dest) is tuple:
        addr_dest = addr_dest,
    elif addr_dest.__len__() != 0:
        if not type(addr_dest[0]) is tuple:
            addr_dest = addr_dest,
    else:
        print(str(addr_dest) + ' it\'s not a valid address')
        return

    for addr_t in addr_dest:
        dev_socket = None
        try:
            if not type(addr_t[0]) is str or not type(addr_t[1]) is int:
                print(str(addr_t) + ' it\'s not a valid address')
                return
            elif addr_t[0] == '':
                return
        except:
            return

        if proto.lower() == 'TCP'.lower():
            dev_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif proto.lower() == 'UDP'.lower():
            dev_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            return

        try:
            dev_socket.connect(addr_t)
            dev_socket.send(str(msg).encode())
            if reply and replyCallback is not None:
                replyCallback(dev_socket.recv(4098))
        except:
            return
        finally:
            dev_socket.close()





# >>> h = ['a','b']
# >>> t = 'a','b'
# >>> s = 'afgh'
# >>> type(h)
# <class 'list'>
# >>> type(t)
# <class 'tuple'>
# >>> type(s)
# <class 'str'>
