# Q35 can only use 2 ide slots and only the master devices, no slave devices (Only IDE 0 and 2, 1 and 3 are slaves)
# i440fx seems to be able to use Both master and slave devices (IDE 0,1,2,3) but macOS doesn't seem to boot on this platform.
# Proxmox ISO folder: /var/lib/vz/template/iso

def WriteConfig(str):
    with open("vm.conf", "a") as write_vmconfig:
        print("IDE BUS for config: " + str)
        #ide0: local:iso/BigSur-recovery.img,cache=unsafe,size=2097012K
        write_vmconfig.write("\n" + str + ": local:iso/BigSur-recovery.img,cache=unsafe")
        print("Added " + str + " for macOS recovery to vm config")

with open ('vm.conf', 'r') as readconf:
    vmconfigcontents =  ("".join(line.strip() for line in readconf))  
    print("vm config contents: \n", vmconfigcontents, "\n")
    
    AllSataAndIdePorts = ["ide0", "ide2", "sata0", "sata1", "sata2", "sata3", "sata4", "sata5", "sata6"]

    if all(x in vmconfigcontents for x in AllSataAndIdePorts):
        print("All SATA ports from 1-5 and IDE ports 0 and 2 are used, please remove a used IDE ro SATA port from the vm")
        exit()

    for port in AllSataAndIdePorts:
        if port not in vmconfigcontents:
            print("Not in VM config: %s" % (port))