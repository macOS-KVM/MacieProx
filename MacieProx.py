# TODO:
# - Add Size to vm config when adding macOS recovery to it
# - Support more, older macOS versions

import os, shutil, subprocess
from pathlib import Path

ScriptPath = "/mnt/MacieProx" # here macrecovery and the downloaded macos reovery will be temporarily stored
macrecoveryPath = "python3 " + ScriptPath + "//macrecovery/macrecovery.py"
ProxISOPath = "/var/lib/vz/template/iso/"
debug = False

def DebugPrint(str):
    if debug == True:
	    print(str)

os.system("clear")

# check if svn (subversion) has been installed
checksvn = subprocess.run(['which', 'svn'], stdout= subprocess.DEVNULL)
if checksvn.returncode == 0:
      DebugPrint("Found svn.")
if checksvn.returncode == 1:
      print("Couldn't find svn")
      print("Please install subverion by running:  apt install subversion")
      print("Once you installed subversion, run this script again")

# debug mode
setdebug = input('\nWould you like to enable debug mode? (default = no) '+ "Options: Y or N \n" )
if setdebug in ['yes', 'Yes', 'Y', 'y']:
  debug = True
  DebugPrint("\nEnabled Debug Mode.")

# Remove existing script folder
if os.path.exists(ScriptPath):
    shutil.rmtree(ScriptPath)
    DebugPrint("\nRemoved existing script folder.")

# Create script storage 
os.mkdir(ScriptPath) 
DebugPrint("\nCreated Script Folder.")

# cd into script storage
os.chdir(ScriptPath) 
DebugPrint("\ncd into script path")

# Clone macrecovery
DebugPrint("\nCloning macrecovery...")
subprocess.run(['svn', 'checkout','https://github.com/acidanthera/OpenCorePkg/trunk/Utilities/macrecovery'], stdout=subprocess.DEVNULL)
DebugPrint("\nCloned macrecovery")

# select macOS version
print("\nWhich macOS version do you want?")
SelectedNumber = input("1. Monterey\n2. Big Sur\n3. Calatina\n4. Mojave\n\nSelect version: ")
if SelectedNumber in ['1']:
    DebugPrint("\nSelected Monterey\n")
    os.system(macrecoveryPath + " -b Mac-E43C1C25D4880AD6 -m 00000000000000000 -os latest download -n macOS-Monterey")
    macOSVersion = "Monterey"
elif SelectedNumber in ['2']:
    DebugPrint("\nSelected Big Sur\n")
    os.system(macrecoveryPath + " -b Mac-2BD1B31983FE1663 -m 00000000000000000 download -n macOS-BigSur")
    macOSVersion = "BigSur"
elif SelectedNumber in ['3']:
    DebugPrint("\nSelected Catalina\n")
    os.system(macrecoveryPath + " -b Mac-00BE6ED71E35EB86 -m 00000000000000000 download -n macOS-Catalina")
    macOSVersion = "Catalina"
elif SelectedNumber in ['4']:
    DebugPrint("\nSelected Mojave\n")
    os.system(macrecoveryPath + " -b Mac-7BA5B2DFE22DDD8C -m 00000000000KXPG00 download -n macOS-Mojave")
    macOSVersion = "Mojave"

DebugPrint("\nConverting macOS-%s.dmg to %s-recovery.img" % (macOSVersion, macOSVersion))
os.system("qemu-img convert macOS-%s.dmg -O raw %s-recovery.img" % (macOSVersion, macOSVersion))
DebugPrint("\nConverted macOS-%s.dmg to %s-recovery.img" % (macOSVersion, macOSVersion))

# check if the macos recovery already exist in the proxmox iso directory
MacRecoveryProxISOPath = ProxISOPath + "%s-recovery.img" % (macOSVersion)
DebugPrint("\nMac Recovery Prox ISO path " + MacRecoveryProxISOPath)
if os.path.exists(MacRecoveryProxISOPath):
    DebugPrint("\nRemoving existing macOS %s recovery from Proxmox ISO folder" % (macOSVersion))
    os.remove(MacRecoveryProxISOPath)

# copy macOS recovery to ISO directory
DebugPrint("\nCommand to move: " + "mv " + macOSVersion + "-recovery.img " + ProxISOPath)
os.system("mv " + macOSVersion + "-recovery.img " + ProxISOPath)
DebugPrint("\nMoved macOS %s recovery to Proxmox ISO folder" % (macOSVersion))

# removing script data folder
shutil.rmtree(ScriptPath)
DebugPrint("\nRemoved script data folder.")

# adding the macOS recovery to a VM
AddRecoveryToVM = input("\n\n\nDo you want to add this macOS recovery to a VM? Default=no " + "Options: Y or N \n")
if AddRecoveryToVM in ['yes', 'Yes', 'Y', 'y']:
    DebugPrint("\nPreparing to add macOS %s recovery to VM" % (macOSVersion))
    # Q35 can only use 2 ide slots and only the master devices, no slave devices (Only IDE 0 and 2, 1 and 3 are slaves)
    # i440fx seems to be able to use Both master and slave devices (IDE 0,1,2,3) but macOS doesn't seem to boot on this platform.
    # Proxmox ISO folder: /var/lib/vz/template/iso
    # Proxmox VM config location: /etc/pve/qemu-server

    vmid = input("\nEnter the vm id of the vm you want to add the macOS recovery to: ")
    DebugPrint("\nChosen vm id: " + vmid)

    vmconfig = "/etc/pve/qemu-server/" + vmid + ".conf"
    DebugPrint("\nChosen vm config loaction" + vmconfig)

    def WriteConfig(port):
        with open(vmconfig, "a") as write_vmconfig:
            #ide0: local:iso/BigSur-recovery.img,cache=unsafe,size=2097012K
            Size = str((os.path.getsize('/var/lib/vz/template/iso/%s-recovery.img' % macOSVersion))/1024).strip(".0") + "K"
            write_vmconfig.write(port + ": local:iso/%s-recovery.img,cache=unsafe,size=%s\n" % (macOSVersion, Size))
            DebugPrint("\nAdded " + port + " for macOS %s recovery to vm config" % (macOSVersion))

    with open (vmconfig, 'r') as readconf:
        vmconfigcontents =  ("".join(line.strip() for line in readconf))
        AllSataAndIdePorts = ["ide0", "ide2", "sata0", "sata1", "sata2", "sata3", "sata4", "sata5", "sata6"]

        if all(x in vmconfigcontents for x in AllSataAndIdePorts):
            print("\nAll SATA ports from 1-5 and IDE ports 0 and 2 are used, please remove a used IDE ro SATA port from the vm")
            exit()

        for port in AllSataAndIdePorts:
            if port not in vmconfigcontents:
                DebugPrint("\nNot in VM config: %s" % (port))
                WriteConfig(port)
                break