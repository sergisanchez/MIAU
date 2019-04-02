#!/usr/bin/python3
# Client test program
import os
import socket, json

print('PID: ' + str(os.getpid()))

ip_server='147.83.159.219'
#port_server=27444
port_server=27016
portSERV = 27020 # localhost port to service attend
#portSERV = 27023 # localhost port to service attend
SERVICE_FE ="SERVICE:FRONTEND"
SERVICE_EM = "SERVICE:EMERGENCY"


mesg= input('INTRO message: "SERVICE:FRONTEND" /"SERVICE:EMERGENCY" ')

try:
    # Connect and send msg
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip_server, portSERV))
    print('Enviando al cliente \'' + str(mesg) + '\'')
    
    client_socket.send((mesg).encode())
    


except Exception as ex:
    print('Unable to connect to the server')
    print(ex)
finally:
    # Close the connection
    client_socket.close()

print('Stoped')
exit(0)
