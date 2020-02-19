import yaml
import random
import time
import os
import sys
import ipaddress
from random import getrandbits
import subprocess
import socket

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind(('', 7070))
serv.listen(5)
home_dir = os.getenv("HOME")

while True:
    bridge = ''
    subnet = ''
    ser_con, addr = serv.accept()
    while True:
        data = ser_con.recv(8192)
        if not data:
            break
        fo = open("su_logs.txt", "a+")
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        fo.write(current_time)
        fo.write("\nReceived request from controller\n")
        bridge += data
        tenant = bridge.split('_')[0]
        file_name = home_dir + "/Cont_IPs/" + bridge + ".yml"
        with open(file_name, 'r') as f:
            doc = yaml.load(f)
            fo.write("opened yml ")
            subnet = doc["subnet"]

        subnet_li = ipaddress.ip_network(unicode(subnet))

        n = 0
        for ip in subnet_li:
            if n == 0:
                n = n+1
                continue
            new_ip = str(ip)

        
        with open(file_name,'r') as file:
            output = yaml.load(file)
            containerslist = output['Containers']
            len_of_containerslist = len(containerslist)
            container_number = len_of_containerslist + 1
            network = output['network']
            new_container = network + "_con" +str(container_number)
            
            #created container -- if possible use an existing image
            os.system("sudo docker run --privileged -itd --name " + new_container + " ln:custcont")
            time.sleep(4)
            print("Container has been successfully created")

            command="docker inspect -f '{{ .NetworkSettings.IPAddress }}' "+ new_container
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
            res = process.communicate()
            mng_ip=res[0].strip()

            output['Containers'].append({new_container:mng_ip})

        #writing to file
        with open(file_name,'w') as file:
            yaml.dump(output,file)


        veth1 = "veth" + tenant + str(random.randrange(1, 10**6))
        veth2 = "veth" + tenant + str(random.randrange(1, 10**6))

        #created veth pair and added it to the bridge
        os.system("ip link add " + veth1 + " type veth peer name " + veth2)
        os.system("brctl addif " + bridge +" "+ veth1)
        os.system("sudo ip link  set "+veth1+" up ")    
        SC1id = "$(sudo docker inspect -f '{{."+"State.Pid"+"}}' "+new_container+")"
        os.system("sudo ip link set dev "+ veth2 + " netns "+ SC1id)
        os.system("sudo nsenter -t "+SC1id+" -n ip link set " +veth2+" up")

        #added ip to container
        os.system("sudo nsenter -t "+SC1id+" -n ip addr add " +new_ip+ " dev " + veth2)

        fo.write("Updated the yml with new ip\n")
        resp = "Done"
        ser_con.send(resp)
        fo.close()
    ser_con.close()
