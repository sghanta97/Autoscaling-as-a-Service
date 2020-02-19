# parse all files in path curpath+/Tenant
import os
import yaml
home_dir = os.getenv("HOME")
path=home_dir+"/Tenant"
#print(path)

os.system("sudo docker build -f container/cust_conts/Dockerfile -t 'ln:custcont' .")

os.system("sudo docker build -f container/contr/Dockerfile -t 'ln:controller' .")

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

# create the provider ns
os.system("sudo python providerns_setup.py")

print(mapping)
for i in mapping:
      print(mapping[i]["hyp1_li"])
      print(mapping[i]["hyp2_li"])
      os.system("sudo python hyp2_tenant_setup.py "+i)


os.system("kill -9 $(lsof -t -i:9090)")
os.system("nohup python container/ip_listener.py &")

os.system("kill -9 $(lsof -t -i:7070)")
os.system("nohup python container_scale_up.py &")

os.system("kill -9 $(lsof -t -i:6060)")
os.system("nohup python cont_scale_down.py &")

os.system("kill -9 $(lsof -t -i:4040)")
os.system("nohup python container/healer.py &")

