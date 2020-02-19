import yaml

file_name = "T1_br.yml"

with open(file_name,'r') as f:
    doc=yaml.load(f)
    print(doc)

#thisdict = {"con2": "22.0.0.2","con3": "21.0.0.3" }

#doc["Containers"]= thisdict

dom_name = []
vm_IPs = []

for i in doc['Containers']:
            print(i)
            for j in i:
                dom_name.append(j)
                vm_IPs.append(i[j])

print(dom_name)
print(vm_IPs)
with open(file_name, 'w') as file:
    yaml.dump(doc,file)
