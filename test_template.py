import subprocess
result=[]
result1= subprocess.check_output('python3 serv_template.py',input='None', shell=True, universal_newlines=True)
result2= subprocess.check_output('python3 serv_template.py',input='None', shell=True, universal_newlines=True)
result.append(result1)
result.append(result2)
print("result: ", result)
result0=eval(result[0])
print(result0['content']['out'])
print("type result0: ",type(result0))
print("type result: ",type(result))