## import modules###############

##Constant definition ##########
KEYNAME='serv_template'
## input ##################
inpt= input()
## body  ####################

content={'out':"exec results ",'input':inpt}
## output #################
out={}
out={'serv_id':KEYNAME,'content':content}
print(out)