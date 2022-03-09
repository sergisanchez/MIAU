# MIAU
run node as AGENT/LEADER:

usage: nodev2.py device role [-h] [-g gpio] [-B BcastIP] [-portUDP portUDP] [-portTCP portTCP] [-v verbose]

                 device: {CAR, BOM, AMB,..} 
                 role: {LEADER,AGENT}
ex: 

$> python3 nodev2.py CAR LEADER -B "10.0.255.255" #A CAR runs as a LEADER

$> python3 nodev2.py AMB AGENT -B "10.0.255.255"  #An Ambulance runs as a AGENT





