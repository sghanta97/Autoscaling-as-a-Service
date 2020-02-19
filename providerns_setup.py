import os
import time

provider_ns = "hyp2_prns"
veth1 = "veth1"
veth2 = "veth2"
gretunnel="gretun"
os.system("sudo ip netns add " + provider_ns)
time.sleep(1)
os.system("sudo ip netns exec "+provider_ns+" echo 1 > /proc/sys/net/ipv4/ip_forward")
os.system("sudo ip netns exec "+provider_ns+" echo 1 > /proc/sys/net/ipv4/conf/all/proxy_arp")
print("Namespaces are succesfully created")
os.system("sudo ip link add " + veth1 + " type veth peer name "+ veth2)
os.system("sudo ip link set " + veth2 + " netns " + provider_ns)
os.system("sudo ip netns exec " + provider_ns + " ip link set dev " + veth2  +" up")
os.system("sudo ip link set dev " + veth1 + " up")
print("added veth pair to namespace")
os.system("sudo ip addr add 172.16.20.3/24 dev "+ veth1)
os.system("sudo ip netns exec " + provider_ns +" ip addr add 172.16.20.2/24 dev " + veth2)
print("assigned ip")
os.system("sudo ip netns exec " + provider_ns + " ip route add 172.16.21.0/24 via 172.16.20.3")
os.system("sudo ip netns exec " + provider_ns + " ip route add 88.88.88.0/24 via 172.16.20.3")
print("added routes")
os.system("sudo ip route add 172.16.21.0/24 via 88.88.88.98")
print("Added route on hypervisor for tennant")
os.system("sudo ip netns exec " + provider_ns + " ip tunnel add " + gretunnel + " mode gre local 172.16.20.2 remote 172.16.21.2")
os.system("sudo ip netns exec " + provider_ns + " ip link set dev " + gretunnel + " up")
os.system("sudo ip netns exec " + provider_ns + " ip addr add 172.16.60.4/24 dev " + gretunnel)

