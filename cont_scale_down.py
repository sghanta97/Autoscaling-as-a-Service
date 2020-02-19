import os
import sys
import yaml
import time
import socket

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind(('0.0.0.0', 6060))
serv.listen(5)
home_dir = os.getenv("HOME")
while True:
    bridge=''
    conn, addr = serv.accept()
    while True:
        data = conn.recv(8192)
        if not data:
            break
        log_file = open("sd_logs.txt", "a+")
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        log_file.write(current_time)
        log_file.write("\nReceived request from controller\n")
        bridge += data


        #we are assuming the yml file  in same directory 
        file_name= home_dir+"/Cont_IPs/"+bridge+".yml"
        with open(file_name,'r') as f:
            doc=yaml.load(f)
        network=doc['network']
        dom_name=[]
        vm_IPs=[]

        for i in doc['Containers']:
            for j in i:
                dom_name.append(j)
                vm_IPs.append(i[j])

        rem_dom=dom_name.pop()
        #delete the container
        os.system("sudo docker stop "+rem_dom)
        os.system("sudo docker rm -v "+rem_dom)
        log_file.write("Destroyed VM " + rem_dom)
        doc['Containers'].pop()

        #write to file
        with open(file_name, 'w') as file:
            yaml.dump(doc,file)
        log_file.write("\nUpdated yml\n")
        log_file.close()
        conn.send(bridge)
    conn.close()
