import pygame, os, threading, socket
from pygame.locals import *
import sys

# ----------------------------------------------
# Constantes, como anchos y largo de pantalla, etc.
# ----------------------------------------------

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

SCREEN_WIDTH = 1330
SCREEN_HEIGHT = 650
DIR_IMG = './img/'
OBS_POS = {'sem1':((467, 253),(False,False)),
           'sem2':((743, 288),(False,False)),
           'sem3':((780, 50),(True,False)),
           'sem4':((23, 50),(False,True)),
           'sem5':((228, 50),(True,False)),
           'sem6':((228, 255),(False,False)),
           'sem7':((505, 610),(False,False)),
           'sem8':((539, 365),(False,True)),
           'sem9':((745, 404),(True,False)),
           'car1':((19, 535),(False,False)),
           'car2':((1135, 16),(False,False)),
           'bui1':((990, 33), (False,False)),
           'bui2':((1269, 50), (False,False)),
           'bui3':((988, 258), (False,False)),
           'bui4':((1269, 243), (False,False)),
           'bui5':((845, 258), (False,False)),
           'bui6':((1269, 425), (False,False)),
           'bui7':((438, 33), (False,False)),
           'buif':((1193, 539), (False,False)),
           }
BKG_POS = {'background':((-368, -253),(False,False)),
           'scene':((60, 50),(False,False)),
           'logo':((827, 387),(False,False))
            }
MSK_IMG = {}
OBS_IMG = {}
BKG_IMG = {}
MSK_MAP = {'sa':None,
           'ma':None
           }

DEVICE_ID = {
    '192.168.4.85':'car1',
    '192.168.4.57':'car2',
    '192.168.4.127':'bui1',
    '192.168.4.132':'bui2',
    '192.168.4.135':'bui3',
    '192.168.4.126':'bui4',
    '192.168.4.130':'bui5',
    '192.168.4.133':'bui6',
    '192.168.4.131':'bui7',
    '192.168.4.75':'buif',
    '192.168.4.121':'sem1',
    '192.168.4.125':'sem2',
    '192.168.4.128':'sem3',
    '192.168.4.124':'sem4',
    '192.168.4.134':'sem5',
    '192.168.4.123':'sem6',
    '192.168.4.120':'sem7',
    '192.168.4.129':'sem8',
    '192.168.4.122':'sem9'
}

LOAD_IMG = {}
TTL_ID = {
    'car1':0,
    'car2':0,
    'bui1':0,
    'bui2':0,
    'bui3':0,
    'bui4':0,
    'bui5':0,
    'bui6':0,
    'bui7':0,
    'buif':0,
    'sem1':0,
    'sem2':0,
    'sem3':0,
    'sem4':0,
    'sem5':0,
    'sem6':0,
    'sem7':0,
    'sem8':0,
    'sem9':0,
    'ma':0,
    'sa':0
}


# Initialize here all the global variables
connected = True          # Program Running ?
serverPort = 27015
thread_recv = None
id_client = 0

held = False
warned_background = False
warned_objects = False
warned_masks = False
car1_moving = False
car2_moving = False


# ----------------------------------------------
# Thread Definitions
# ----------------------------------------------

def th_reciver():
    # Este thread recibe conexiones entrantes y crea un thread para procesarlas.
    tag=bcolors.OKBLUE+'[recv]: '+bcolors.ENDC
    print(tag + 'Started reciver module')
    global serverSocket
    global id_client

    # Listen for new connections
    serverSocket.listen(1)
    while connected:
        try:
            (connectionsocket, clientAddress) = serverSocket.accept()
            print(tag+'New connection - '+str(clientAddress))
            # Create new thread for each new connection
            t = threading.Thread(target=th_client, args=(id_client, connectionsocket))
            t.start()
            id_client+=1
        except Exception as excep:
            print(bcolors.FAILH + 'ERROR' + bcolors.ENDCH + 'Wellcome fail')
            print(excep)
            return

    print(tag + 'Stoped reciver module')
    return


def th_client(id, clientSocket):
    tag = bcolors.OKBLUE + '[client'+str(id_client)+']: ' + bcolors.ENDC
    print(tag + 'Started client')
    devices = tuple()     # Optional

    try:
        # Recive msg from client
        msg = (clientSocket.recvfrom(2048))[0].decode('utf-8')
        print(tag + 'recv msg \''+msg+'\'')
        devices = eval(msg)
        print(devices)
        for device in devices:
            print(device[0])
            if device[0] in DEVICE_ID.keys():
                # We have a representation for that device
                if device[1] == 'sa' or device[1] == 'ma':
                    increment_TTL(device[1])
                    select_role(DEVICE_ID.get(device[0]),device[1])
                else:
                    increment_TTL(DEVICE_ID.get(device[0]))
                    changeStatusRepresentation(DEVICE_ID.get(device[0]), device[1])

        if msg == 'GREEN': # TODO: WTF is this?!
            print(bcolors.ERROR+'action requiered!')
    except Exception as ex:
        print(bcolors.FAILH + 'ERROR' + bcolors.ENDCH + 'Connection lost...')
        print(ex)
        clientSocket.close()
        return

    print(tag + 'Stoped client')
    return


# ----------------------------------------------
# Clases y Funciones utilizadas
# ----------------------------------------------

def createServer():
    global serverPort
    global serverSocket

    # Server Set-up
    try:
        # Setup IPv4 TCP socket
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # the SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state,
        # without waiting for its natural timeout to expire
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Specify the welcoming port of the server
        serverSocket.bind(('', serverPort))
        print(bcolors.OKGREENH+'OK'+bcolors.ENDCH+'Server created.')
    except Exception as ex:
        print(bcolors.FAILH + 'ERROR' + bcolors.ENDCH + 'Can\'t create the socket. '
                                                        'Maybe you have another server at the same port?')
        print(ex)
        exit(-1)


def threadingSetup():
    global thread_recv

    thread_recv = threading.Thread(target=th_reciver,daemon=True)

    print(bcolors.OKGREENH+'OK'+bcolors.ENDCH+'Threads ready to start.')


def startThreads():
    global thread_recv
    try:
        thread_recv.start()
    except Exception as ex:
        print(bcolors.FAILH + 'ERROR' + bcolors.ENDCH + 'Thread can not start.')
        print(ex)
        exit(-1)


def load_image(nombre, dir_imagen=DIR_IMG, alpha=False):
    # Encontramos la ruta completa de la imagen

    if nombre in LOAD_IMG.keys():
        image = LOAD_IMG.get(nombre)
    else:
        print(bcolors.ERROR + "Can\'t load the image: " + nombre)
        return None
    return image


def load_image_f(nombre, dir_imagen=DIR_IMG, alpha=False):
    # Encontramos la ruta completa de la imagen
    ruta = os.path.join(dir_imagen, nombre)
    try:
        image = pygame.image.load(ruta)
    except:
        print(bcolors.ERROR + "Can\'t load the image: " + ruta)
        sys.exit(1)
    # Comprobar si la imagen tiene "canal alpha" (como los png)
    if alpha is True:
        image = image.convert_alpha()
    else:
        image = image.convert()
    return image


def preload_all_image_resources():
    global LOAD_IMG
    l = list()      # (hash_key, file_name.ext, alpha)
    print(bcolors.OKBLUE + 'Loading resources...' + bcolors.ENDC)

    # Background (Special Case)
    l.append(('background', 'back.jpg', False))
    l.append(('scene', 'Diagram-color.gif', True))
    l.append(('logo', 'craax.png', True))
    # Images (General Case)
    l.append(('building.png', 'building.png', True))
    l.append(('building_ma.png', 'building_ma.png', True))
    l.append(('building_sa.png', 'building_sa.png', True))
    l.append(('buildingf.png', 'buildingf.png', True))
    l.append(('buildingf-f.png', 'buildingf-f.png', True))
    l.append(('buildingh.png', 'buildingh.png', True))
    l.append(('buildingh_ma.png', 'buildingh_ma.png', True))
    l.append(('buildingh_sa.png', 'buildingh_sa.png', True))
    l.append(('car.png', 'car.png', True))
    l.append(('car-g.png', 'car-g.png', True))
    l.append(('car-r.png', 'car-r.png', True))
    l.append(('carh.png', 'carh.png', True))
    l.append(('carh-g.png', 'carh-g.png', True))
    l.append(('carh-r.png', 'carh-r.png', True))
    l.append(('sem.png', 'sem.png', True))
    l.append(('sem-g.png', 'sem-g.png', True))
    l.append(('sem-r.png', 'sem-r.png', True))
    l.append(('semh.png', 'semh.png', True))
    l.append(('semh-g.png', 'semh-g.png', True))
    l.append(('semh-r.png', 'semh-r.png', True))
    # Masks (General Case)
    l.append(('car_ma_mask.png', 'car_ma_mask.png', True))
    l.append(('car_sa_mask.png', 'car_sa_mask.png', True))
    l.append(('carh_ma_mask.png', 'carh_ma_mask.png', True))
    l.append(('carh_sa_mask.png', 'carh_sa_mask.png', True))
    l.append(('sem_ma_mask.png', 'sem_ma_mask.png', True))
    l.append(('sem_sa_mask.png', 'sem_sa_mask.png', True))
    l.append(('semh_ma_mask.png', 'semh_ma_mask.png', True))
    l.append(('semh_sa_mask.png', 'semh_sa_mask.png', True))

    i = 0
    for obj in l:
        LOAD_IMG.update({obj[0]:load_image_f(obj[1],alpha=obj[2])})
        i+=1

    print(bcolors.OKGREEN + 'Successfully loaded ' + str(i) + ' resources.' + bcolors.ENDC)


def draw_all_objects(screen):
    global warned_objects
    try:
        for object_k in OBS_IMG.keys():
            if object_k in OBS_POS.keys():
                object_img = OBS_IMG.get(object_k)
                object_pos = OBS_POS.get(object_k)[0]
                object_flip = OBS_POS.get(object_k)[1]
                object_img = pygame.transform.flip(object_img, object_flip[0], object_flip[1])
                screen.blit(object_img, object_pos)
            else:
                print('Position for ' + object_k + ' not found.')
    except Exception as ex:
        if not warned_objects:
            print(bcolors.ERROR + 'Draw all objects process failed.')
            warned_objects = True


def draw_all_masks(screen):
    global warned_masks
    try:
        for object_k in MSK_IMG.keys():
            if object_k in MSK_MAP.keys() and MSK_MAP.get(object_k) is not None:
                object_img = MSK_IMG.get(object_k)
                object_pos = OBS_POS.get(MSK_MAP.get(object_k))[0]
                object_flip = OBS_POS.get(MSK_MAP.get(object_k))[1]
                object_img = pygame.transform.flip(object_img, object_flip[0], object_flip[1])
                screen.blit(object_img, object_pos)
            else:
                print('Position for ' + object_k + ' not found.')
    except Exception as ex:
        if not warned_masks:
            print(bcolors.ERROR + 'Draw all masks process failed.')
            warned_masks = True


def load_all_masks():
    for mask in MSK_MAP.keys():
        if MSK_MAP.get(mask) is not None:
            name = MSK_MAP.get(mask)
            fail = False
            if str(name).__len__() < 4:
                pass
            else:
                if str(name[3:]) == 'f':
                    flip = 'f'
                elif int(name[3:]) % 2 == 0:
                    flip = ''
                else:
                    flip = 'h'

            if str(name)[0:3] == 'sem':
                basename = 'sem'
                exten = '_mask.png'
            elif str(name)[0:3] == 'car':
                basename = 'car'
                exten = '_mask.png'
            elif str(name)[0:3] == 'bui':
                basename = 'building'
                exten = '.png'
            else:
                # basename = ''
                # exten = '.png'
                fail = True

            if not fail:
                # print(basename + flip + '_' + mask + exten)
                MSK_IMG.update({mask: load_image(basename + flip + '_' + mask + exten, alpha=True)})


def load_all_objects():
    global OBS_IMG
    exten = '.png'
    for name in OBS_POS.keys():
        if str(name).__len__() < 4:
            pass
        else:
            if str(name[3:]) == 'f':
                flip = 'f'
            elif int(name[3:]) % 2 == 0:
                flip = ''
            else:
                flip = 'h'

        if str(name)[0:3] == 'sem':
            basename = 'sem'
        elif str(name)[0:3] == 'car':
            basename = 'car'
        elif str(name)[0:3] == 'bui':
            basename = 'building'
        else:
            basename = ''
        OBS_IMG.update({name: load_image(basename+flip+exten, alpha=True)})


def load_background():
    global BKG_IMG
    fondo = load_image('background')
    escenari = load_image('scene')
    logo = load_image('logo')
    BKG_IMG.update({'background':fondo, 'scene':escenari, 'logo':logo})


def select_role(device, role):
    global MSK_MAP
    if role == 'sa':
        if device == MSK_MAP.get('ma'):
            MSK_MAP['ma'] = None
            if 'ma' in MSK_IMG.keys():
                del(MSK_IMG['ma'])
    elif role == 'ma':
        if device == MSK_MAP.get('sa'):
            MSK_MAP['sa'] = None
            if 'sa' in MSK_IMG.keys():
                del (MSK_IMG['sa'])

    MSK_MAP[role] = device
    load_all_masks()


def draw_background(screen):
    global warned_background
    try:
        screen.fill([255, 255, 255])
        for object_k in BKG_IMG.keys():
            if object_k in BKG_POS.keys():
                object_img = BKG_IMG.get(object_k)
                object_pos = BKG_POS.get(object_k)[0]
                object_flip = BKG_POS.get(object_k)[1]
                object_img = pygame.transform.flip(object_img, object_flip[0], object_flip[1])
                screen.blit(object_img, object_pos)
            else:
                print('Position for ' + object_k + ' not found.')
    except Exception as ex:
        if not warned_background:
            print(bcolors.ERROR + 'Draw background process failed.')
            warned_background = True


def changeStatusRepresentation(object_k, status_msg):
    global car1_moving, car2_moving
    srt = ''
    if object_k[0:3] == 'sem':
        srt = 'sem'
        if int(object_k[3:])%2 == 0:
            # Sem0, sem2, sem4....
            srt +=''
        else:
            # sem1, sem3, sem5.....
            srt += 'h'

        if status_msg == 'GREEN':
            srt += '-g'
        elif status_msg == 'RED':
            srt += '-r'
    elif object_k[0:3] == 'car':
        srt = 'car'
        if int(object_k[3:]) % 2 == 0:
            # car0, car2, car4....
            srt += ''
        else:
            # car1, car3, car5.....
            srt += 'h'

        if status_msg == 'START':
            srt += '-g'
            if object_k == 'car1':
                car1_moving = True
            elif object_k == 'car2':
                car2_moving = True
        elif status_msg == 'STOP':
            srt += '-r'
            if object_k == 'car1':
                car1_moving = False
            elif object_k == 'car2':
                car2_moving = False

    elif object_k[0:3] == 'bui':
        srt = 'building'
        if str(object_k[3:]) == 'f':
            srt += 'f'
        elif int(object_k[3:]) % 2 == 0:
            # car0, car2, car4....
            srt += ''
        else:
            # car1, car3, car5.....
            srt += 'h'

        if status_msg == 'MA':
            srt += '-g'
        elif status_msg == 'SA':
            srt += '-r'
        elif status_msg == 'FIRE':
            srt += '-f'

    print('img: ' + srt)
    OBS_IMG[object_k] = load_image(srt+'.png', alpha=True)

    # if (object_k == 'sem1'): # Codi lasanya amb macarrons
    #     OBS_IMG['sem3'] = load_image(srt + '.png', alpha=True)


def animate_cars():
    car1_pos_final = (1135,535)
    car2_pos_final = (1135,480)

    if OBS_POS.get('car1')[0][0] < car1_pos_final[0] and car1_moving:
        OBS_POS.update({'car1':((OBS_POS.get('car1')[0][0]+3, OBS_POS.get('car1')[0][1]),OBS_POS.get('car1')[1])})
    if OBS_POS.get('car2')[0][1] < car2_pos_final[1] and car2_moving:
        OBS_POS.update({'car2': ((OBS_POS.get('car2')[0][0], OBS_POS.get('car2')[0][1] + 2), OBS_POS.get('car2')[1])})


def reducce_TTL():
    global TTL_ID
    for key in TTL_ID.keys():
        if int(TTL_ID.get(key)) == 0:
            # Necesita eliminar la representacion
            if key == 'sa' or key == 'ma':
                select_role('fro0', key)
                pass
            else:
                changeStatusRepresentation(key, 'NONE')

        TTL_ID[key] = int(TTL_ID.get(key))-1


def increment_TTL(key):
    global TTL_ID
    if key in TTL_ID.keys():
        TTL_ID[key] = 800


def main_windows():
    global connected, held, MSK_MAP
    pygame.init()
    # La clase o función principal que crea o ejecuta la interfaz
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_icon(pygame.image.load(DIR_IMG+'car.ico'))

    preload_all_image_resources()
    load_background()
    load_all_objects()
    load_all_masks()

    pygame.display.flip()

    while connected:
        # Posibles entradas del teclado y mouse
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                connected = False
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    connected = False
                if event.key == K_r:
                    for name in OBS_IMG.keys():
                        if name[0:3] == 'sem':
                            if int(name[3:]) % 2 == 0:
                                changeStatusRepresentation(name,'GREEN')
                                increment_TTL(name)
                            else:
                                changeStatusRepresentation(name, 'RED')
                                increment_TTL(name)
                if event.key == K_g:
                    for name in OBS_IMG.keys():
                        if name[0:3] == 'sem':
                            if int(name[3:]) % 2 == 0:
                                changeStatusRepresentation(name,'RED')
                            else:
                                changeStatusRepresentation(name, 'GREEN')
                if event.key == K_c:
                    del(OBS_IMG['car1'])
                if event.key == K_t:
                    select_role('sem1', 'sa')
                    load_all_masks()
                if event.key == K_y:
                    select_role('sem1', 'ma')
                    load_all_masks()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                held = True
            elif event.type == pygame.MOUSEBUTTONUP:
                held = False

        if held:
            OBS_POS['car2'] = ((pygame.mouse.get_pos()[0]-10,pygame.mouse.get_pos()[1]-10),(False,False))
            print(str((pygame.mouse.get_pos()[0]-10,pygame.mouse.get_pos()[1]-10)))

        animate_cars()
        reducce_TTL()
        draw_background(screen)
        draw_all_objects(screen)
        draw_all_masks(screen)
        pygame.display.update()

    print(bcolors.OKGREEN + 'PID: ' + str(os.getpid()) + ' it\'s stoping...' + bcolors.ENDC)
    exit(0)

if __name__ == "__main__":
    print(bcolors.OKGREEN + 'PID: ' + str(os.getpid()) + bcolors.ENDC)
    createServer()
    threadingSetup()
    startThreads()
    main_windows() # Last operation before start UI
