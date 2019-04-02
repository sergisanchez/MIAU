import requests

response=(requests.get('http://147.83.159.220:8000/get_topoDB')).json()
print("num:",response[1],'\n' )
response=eval(response[0])

for elem in response:
    del elem['_id']
    print(elem)
