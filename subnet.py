import sys
import os
import random
import ipaddress
import subprocess
from random import getrandbits
import yaml

bridge=sys.argv[1]
provider_ns="hyp2_prns" #final add

home_dir = os.getenv("HOME")
path=home_dir+"/Tenant/"+bridge+".yml"
c_config = yaml.load(open(path))
Tenant= c_config['t_name']
subnet= c_config['subnet']
min_con= c_config['min_containers']

assigned_ips = set()

con_list = []
thisdict={}
lofdict = []
#os.system("sudo docker build -t 'ln:hw5' .")
for i in range(int(min_con)+1):
    if i == 0:
        os.system("sudo docker run --privileged -itd --hostname "+bridge+" --name=" + bridge + "_con" + str(i) + " ln:controller")
    else:
        os.system("sudo docker run --privileged -itd --name=" + bridge + "_con" + str(i) + " ln:custcont")
    if i != 0:
       con_list.append(bridge + "_con" + str(i))

print("Created containers")

os.system("sudo brctl addbr " + bridge)
os.system("sudo ip link set "+bridge+" up")
print("Created Bridge")

cont_ip_list=[]         #changed here
for container in con_list:
    thisdict = {}
    veth_one_end =  bridge + "_" + str(random.randrange(1, 10**6))
    veth_other_end = bridge + "_" + str(random.randrange(1, 10**6))
    #print(veth_one_end)
    #print(veth_other_end)
    os.system("ip link add " + veth_one_end + " type veth peer name " + veth_other_end)
    os.system("brctl addif " + bridge +" "+ veth_one_end)
    os.system("sudo ip link set dev "+ veth_one_end +" up")
    SC1id = "$(sudo docker inspect -f '{{."+"State.Pid"+"}}' "+str(container)+")"
    os.system("sudo ip link set dev "+ veth_other_end + " netns "+ SC1id)
    os.system("sudo nsenter -t "+SC1id+" -n ip link set " +veth_other_end+" up")
    #os.system("sudo nsenter -t "+SC1id+" -n ip addr add "+new_ip )
    os.system("sudo nsenter -t "+SC1id+" -n ip route del default")
    os.system("sudo nsenter -t "+SC1id+" -n ip route add default dev "+veth_other_end)
    subnet_range = ipaddress.ip_network(unicode(subnet))
    n = 0
    for ip in subnet_range:
        if n <= 1:
            n = n + 1
            continue
        if str(ip) not in assigned_ips:
            ip = str(ip)
            assigned_ips.add(str(ip))
            break
        print()
    n = 0
    cont_ip_list.append(ip)      #changed here
    os.system("sudo docker exec -it "+container+ " ip addr add "+ip+" dev " +veth_other_end)
    
    command="docker inspect -f '{{ .NetworkSettings.IPAddress }}' "+ container
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
    output = process.communicate()
    mng_ip=output[0][0:len(output[0])-1]
    print("Guderian")
    print(mng_ip)
    thisdict[container]=mng_ip
    print(thisdict)
    lofdict.append(thisdict)



file=home_dir + "/Tenant/" + bridge + '.yml'
with open(file,'r') as f:
     die=yaml.load(f)

public_ip=die['public_ip'] #final add

#create veth pair for connection to namespace
tenant_name=bridge.split("_")[0]
veth1=bridge+"_v1"
veth2=bridge+"_v2"
print("debug1")
os.system("ip link add " + veth1 + " type veth peer name " + veth2)
print("debug2")
os.system("sudo ip link set "+veth1+" netns "+tenant_name+"_ns")
print("debug3")
os.system("sudo ip netns exec "+tenant_name+"_ns"+" ip link set dev "+veth1+" up")
os.system("sudo ip netns exec "+tenant_name+"_ns"+" ip addr add "+public_ip+" dev "+veth1) #added final
os.system("sudo ip netns exec "+provider_ns+" ip route add "+public_ip+"/32 dev "+tenant_name + "_v1") #fianl added
print("debug4")
os.system("brctl addif " + bridge +" "+ veth2)
os.system("sudo ip link set dev "+veth2+" up")
print("debug5")
os.system("sudo ip netns exec "+tenant_name+"_ns"+" ip route add "+subnet+" dev "+veth1)
print("debug6")

##
'''
file_name=home_dir + "/Cont_IPs/" + bridge + '.yml'
with open(file_name,'r') as f:
     doc=yaml.load(f)
     doc["Containers"] = lofdict
print(doc)
#doc["Containers"]= lofdict

with open(file_name, 'w+') as file:
      yaml.dump(doc,file)
t_file = home_dir + "/" + bridge + ".yml"
with open(t_file, 'w+') as file:
      yaml.dump(doc,file)

'''


file_name=home_dir + "/Cont_IPs/" + bridge + '.yml'
with open(file_name,'r') as f:
     doc=yaml.load(f)

doc["Containers"]= lofdict

with open(file_name, 'w') as file:
      yaml.dump(doc,file)





############load balancing################
Tennant=tenant_name
num=len(cont_ip_list)
val= 1/float(num)
i=cont_ip_list.pop()
for j in cont_ip_list:
     os.system("sudo ip netns exec "+Tennant+"_ns iptables -t nat -A PREROUTING -p icmp -d "+public_ip+" -m statistic --mode random --probability "+str(val)+" -j DNAT --to-destination "+j)
os.system("sudo ip netns exec "+Tennant+"_ns iptables -t nat -A PREROUTING -p icmp -d "+public_ip+" -m statistic --mode random --probability 1 -j DNAT --to-destination "+i)
print("Added iptable rules to balance load inside a Linux server")
