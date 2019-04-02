import json
import random

d = {
    'id_source' : '123',
    'id_destination' : '456',
    'op_code' : '120',
    'timestamp' : '121846312',

}
d1 = {
    'id_source': '567',
    'id_destination': '890',
    'op_code': '888',
    'timestamp': '0000000',

}

# Crear JSON
js = json.dumps(d)
print(js)
js1=json.dumps(d1)
# Decodificar JSON recv
rjs = json.loads(js)
rjs1 = json.loads(js1)
rjs['op_code']=(rjs['op_code'],rjs1['op_code'])
# Leer un campo
for code in rjs['op_code']:
   print(code)
print(rjs)
js2= json.dumps(rjs)
print(rjs)
print(rjs['op_code'])