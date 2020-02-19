import os
import sys
import ast
import yaml

tenant = sys.argv[1]

home_dir = os.getenv("HOME")
path=home_dir+"/Tenant"
#print(path)

#print(path)
files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if '.yml' in file:
            files.append(os.path.join(r, file))

mapping={}
for f in files:
    c_config = yaml.load(open(f))
    Tenant=c_config['t_name']
    if Tenant not in mapping:
        mapping[Tenant]={"hyp1_li":[],"hyp2_li":[]}
    hyp=c_config['hyp']
    network=c_config["nw_name"]
    if hyp == "hyp_1":
       mapping[Tenant]["hyp1_li"]=mapping[Tenant]["hyp1_li"]+[network]
    else:
       mapping[Tenant]["hyp2_li"]=mapping[Tenant]["hyp2_li"]+[network]

print(mapping)

tenant_ns = tenant + "_ns"

provider_ns = "hyp2_prns"

os.system("sudo ip netns add " + tenant_ns)
print("Create namespace for " + tenant)

os.system("sudo ip netns exec "+tenant_ns+" echo 1 > /proc/sys/net/ipv4/ip_forward")
os.system("sudo ip netns exec "+tenant_ns+" echo 1 > /proc/sys/net/ipv4/conf/all/proxy_arp")


tns_command = "sudo ip netns exec " + tenant_ns + " "

veth1 = tenant + "_v1"
veth2 = tenant + "_v2"
os.system("sudo ip link add " + veth1 + " type veth peer name " + veth2)

print("Create veth pairs")

os.system("sudo ip link set dev " + veth1 + " netns " + provider_ns)
os.system("sudo ip link set dev " + veth2 + " netns " + tenant_ns)

print("Moved veths")

os.system("sudo ip netns exec " + provider_ns + " ip link set dev " + veth1 + " up")
os.system("sudo ip netns exec " + tenant_ns + " ip link set dev " + veth2 + " up")

print("Set veths up")


ip1 = ""
ip2 = ""
tunnel_ip = ""
tenant_other_subnet = ""
tenant_gre_remote = ""

subnet_mask = "/24"

if tenant == "T1":
    ip1 = "172.16.22.2"
    ip2 = "172.16.22.3"
    tunnel_ip = "172.16.50.2"
    tenant_other_subnet = "172.16.23.0/24"
    tenant_gre_remote = "172.16.23.3"
else:
    ip1 = "172.16.32.2"
    ip2 = "172.16.32.3"
    tunnel_ip = "172.16.50.4"
    tenant_other_subnet = "172.16.33.0/24"
    tenant_gre_remote = "172.16.33.3"

os.system("sudo ip netns exec " + provider_ns + " ip addr add " + ip1 + subnet_mask + " dev " + veth1)
os.system("sudo ip netns exec " + tenant_ns + " ip addr add " + ip2 + subnet_mask  + " dev " + veth2)

print("Added IPs")

os.system("sudo ip netns exec " + tenant_ns  + " ip route add default via " + ip1)
os.system("sudo ip netns exec " + provider_ns + " ip route add " + tenant_other_subnet + " dev gretun")

print("Added default route in ts and gre route in prns")

tenant_tunnel = tenant + "_tunnel"

os.system(tns_command +  "ip tunnel add " + tenant_tunnel + " mode gre remote " + tenant_gre_remote + " local " + ip2)
os.system(tns_command + "ip link set " + tenant_tunnel + " up")
os.system(tns_command + "ip addr add " + tunnel_ip + subnet_mask +" dev " + tenant_tunnel)


#edit
for i in mapping:
    if i == tenant:
       for j in mapping[i]['hyp2_li']:
          output= yaml.load(open(f))
          c_dict={}
          c_dict["max_containers"]=output["max_containers"]
          c_dict["min_containers"]=output["min_containers"]
          c_dict["network"]=output["nw_name"]
          c_dict["threshold"]=output["threshold"]
          c_dict["subnet"]=output["subnet"]
          with open(home_dir + "/Cont_IPs/" + j + '.yml', 'w+') as outfile:
                 yaml.dump(c_dict, outfile, default_flow_style=False)


for i in mapping:
    if i== tenant:
            for j in mapping[i]["hyp2_li"]:
                  os.system("sudo python subnet.py "+j)
#new edit
mapping= {}
for f in files:
    c_config = yaml.load(open(f))
    Tenant=c_config['t_name']
    if Tenant not in mapping:
        mapping[Tenant]={"hyp1_li":[],"hyp2_li":[]}
    hyp=c_config['hyp']
    subnet=c_config["subnet"]
    if hyp == "hyp_1":
       mapping[Tenant]["hyp1_li"]=mapping[Tenant]["hyp1_li"]+[subnet]
    else:
       mapping[Tenant]["hyp2_li"]=mapping[Tenant]["hyp2_li"]+[subnet]



#if Tenantname matches:
#  then add route for all subnets in hyp2 via  veth1 [provi 

#if Tenantname matches:
#  then add route for all subnets in hyp1 li  via gretun [Tenantns] 

for i in mapping:
   if i == tenant:
      for j in mapping[i]:
        if j=="hyp1_li":
           for sub in mapping[i][j]:
               os.system("sudo ip netns exec "+tenant_ns+" ip route add "+sub+" dev "+tenant_tunnel)

