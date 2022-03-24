from ast import Add
import os, shutil
from pathlib import Path

ScriptPath = "/mnt/MacieProx"
macrecoveryPath = "python3 " + ScriptPath + "/OpenCorePkg/Utilities/macrecovery/macrecovery.py"
ProxISOPath = "/var/lib/vz/template/iso/"
debug = False

def DebugPrint(str):
    if debug == True:
	    print(str)

os.system("clear")

# debug mode
setdebug = input('\nWould you like to enable debug mode? (default = no) '+ "Options: Y or N \n" )
if setdebug in ['yes', 'Yes', 'Y', 'y']:
  debug = True
  DebugPrint("\nEnabled Debug Mode.")

# Remove existing script folder
if os.path.exists(ScriptPath):
    shutil.rmtree(ScriptPath)
    DebugPrint("\nRemoved existing script folder.")

os.mkdir(ScriptPath) # Create script folder
DebugPrint("\nCreated Script Folder.")
os.chdir(ScriptPath) # cd into script path
DebugPrint("\ncd into script path\n")
os.system("git clone https://github.com/acidanthera/OpenCorePkg.git") # Clone OpenCore
DebugPrint("\nCloned OpenCore\n")

# select macOS version
print("Which macOS version do you want?")
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

os.system("qemu-img convert macOS-%s.dmg -O raw %s-recovery.img" % (macOSVersion, macOSVersion))
DebugPrint("\nConverted macOS-%s.dmg to %s-recovery.img" % (macOSVersion, macOSVersion))

# remove macOS-XX.dmg and macOS-XX.chunklist 
os.remove(ScriptPath + "/macOS-%s.dmg" % (macOSVersion))
DebugPrint("\nRemoved macOS-%s.dmg" % (macOSVersion))
os.remove(ScriptPath + "/macOS-%s.chunklist" % (macOSVersion))
DebugPrint("\nRemoved macOS-%s.chunklist" % (macOSVersion))

# check if the macos recovery already exist in the proxmox iso directory
MacRecoveryProxISOPath = ProxISOPath + "%s-recovery.img" % (macOSVersion)
DebugPrint("Mac Recovery Prox ISO path " + MacRecoveryProxISOPath)
if os.path.exists(MacRecoveryProxISOPath):
    DebugPrint("\nRemoving existing macOS %s recovery from Proxmox ISO folder" % (macOSVersion))
    os.remove(MacRecoveryProxISOPath)

# copy macOS recovery to ISO directory
DebugPrint("\nCommand to move: " + "mv " + macOSVersion + "-recovery.img " + ProxISOPath)
os.system("mv " + macOSVersion + "-recovery.img " + ProxISOPath)
DebugPrint("\nMoved macOS %s recovery to Proxmox ISO folder" % (macOSVersion))

# adding the macOS recovery to a VM
AddRecoveryToVM = input("\n\n\nDo you want to add this macOS recovery to a VM? Default=no")
if AddRecoveryToVM in ['yes', 'Yes', 'Y', 'y']:
    DebugPrint("Preparing to add macOS %s recovery to VM" % (macOSVersion))
    VMID = input("Enter the VM ID of the vm you want the macOS recovery to")
    VM_config = open("vm.conf")
    VM_config.write("test")