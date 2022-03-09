import pysftp
#testing sftp conection with chanin server
myHostname = "10.0.0.48"
myUsername = "root"
remoteFilePath = "/root/MIAU_devlpmt/pyServices/amb.py"
localFilePath = "./execode.py"
with pysftp.Connection(host=myHostname, username=myUsername) as sftp:
    print ("Connection succesfully stablished ... ")
    sftp.get(remoteFilePath,localFilePath)