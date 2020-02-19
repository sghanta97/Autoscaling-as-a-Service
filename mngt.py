import os
import subprocess

con_name = "T1_br1_con2"

result = subprocess.getoutput("sudo docker inspect -f '{{ .NetworkSettings.IPAddress }}' " + con_name)
print(result)  
