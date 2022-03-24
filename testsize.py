import os
# Proxmox ISO folder: /var/lib/vz/template/iso

SizeBytes = os.path.getsize('C:/Users/Stijn Rombouts/BigSurRec.img') 

SizeKiloBytes = str(SizeBytes/1024).strip(".0") #remove .0 from calculation

print('Size of file is', SizeKiloBytes, 'bytes')