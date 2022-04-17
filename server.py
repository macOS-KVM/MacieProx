# NOTE: if you're getting OSError: [Errno 98] Address already in use:
# Use: ps -fA | grep python    (first number is the id)
# then: kill $id

# TODO: Set port with an optional argument of the script

import socket, os
from time import sleep
from subprocess import Popen, PIPE, STDOUT

# create and configure socket on local host
serverSocket = socket.socket()
host = ''
port = 26 #arbitrary port
serverSocket.bind((host, port))
serverSocket.listen(1)

con, addr = serverSocket.accept()
ProxISOPath = "/var/lib/vz/template/iso/"

def DebugWrite(dbg_message):
    print("DEBUG:", dbg_message)

DebugWrite("Connected")

def MoveToProxISOFolder(macOSVersion):
    macOSVersion = str(macOSVersion)
    MacRecoveryProxISOPath = str(ProxISOPath + "%s-recovery.img" % (macOSVersion))
    DebugWrite("Mac Recovery Prox ISO path " + MacRecoveryProxISOPath)
    con.send("\nMac Recovery Prox ISO path ".encode() + MacRecoveryProxISOPath.encode())
    if os.path.exists(MacRecoveryProxISOPath):
        DebugWrite("Removing existing macOS %s recovery from Proxmox ISO folder" % (macOSVersion))
        con.send("Removing existing macOS ".encode() + macOSVersion.encode() + " recovery from Proxmox ISO folder".encode())
        os.remove(MacRecoveryProxISOPath)
    # copy macOS recovery to ISO directory
    mv_command = str("mv " + macOSVersion + "-recovery.img " + ProxISOPath)
    DebugWrite("Command to move: " + mv_command)
    con.send("\nCommand to move: mv ".encode() + mv_command.encode())
    os.system(mv_command)
    con.send("\nMoved macOS ".encode() + macOSVersion.encode() +  " recovery to Proxmox ISO folder".encode())
    DebugWrite("Moved macOS " + macOSVersion + " recovery to Proxmox ISO folder")

def ConvertIMG(macOSVersion):
    DebugWrite("Converting macOS-%s.dmg to %s-recovery.img" % (macOSVersion, macOSVersion))
    os.system("qemu-img convert macOS-%s.dmg -O raw %s-recovery.img" % (macOSVersion, macOSVersion))
    DebugWrite("Converted macOS-%s.dmg to %s-recovery.img" % (macOSVersion, macOSVersion))

def CheckSvnInstalled(): # check if svn (subversion) has been installed
    checksvn = Popen("which svn", stdout = PIPE, stderr = STDOUT, shell = True, text=True)
    checksvnout = checksvn.stdout.readline()
    if checksvnout == "":
        con.send("It looks like svn isn't installed. I'll install it for you!\n".encode())
        installsvn = Popen("apt install subversion -y", stdout = PIPE, stderr = STDOUT, shell = True, text=True)
        while True:
            line = installsvn.stdout.readline()
            con.send(b"svn install said: " + line.encode())
            if not line:
                con.send("Done installing svn\n".encode())
                break
    elif checksvnout != "":
        con.send("svn is installed at: ".encode() + checksvnout.encode() + "\n".encode())

def CloneMacRec():
    os.chdir('/root/') # avound the current directory still being /root/macrecovery when downloading macOS multiple times
    if os.path.exists('/root/macrecovery'):
        DebugWrite("An existing copy of macrecovery was already found. I won't clone macrecovery again.")
    else:
        DebugWrite("Cloning macrecovery...")
        clonemacrecovery = Popen("svn checkout https://github.com/acidanthera/OpenCorePkg/trunk/Utilities/macrecovery", stdout = PIPE, stderr = STDOUT, shell = True, text=True)
        while True:
            line = clonemacrecovery.stdout.readline()
            con.send(b"macrecovery: " + line.encode())
            if not line:
                DebugWrite("Done Cloning macrecovery")
                con.send("Done Cloning macrecovery\n".encode())
                break

def getmacOS(macOSVersion):
    CheckSvnInstalled()
    CloneMacRec()
    try:
        os.chdir("/root/macrecovery")
        DebugWrite("Cd into macrecovery directory")
    except:
        DebugWrite("failed to cd into the macrecovery directory")
        DebugWrite("Current directory: " + os.getcwd())
    MacRecoveryPath = 'python3 ./macrecovery.py'
    if macOSVersion == "Monterey":
        macrec = Popen(MacRecoveryPath + " -b Mac-E43C1C25D4880AD6 -m 00000000000000000 -os latest download -n macOS-Monterey", stdout = PIPE, stderr = STDOUT, shell = True, text=True)
    elif macOSVersion == "Big Sur":
        macrec = Popen(MacRecoveryPath + " -b Mac-2BD1B31983FE1663 -m 00000000000000000 download -n macOS-BigSur", stdout = PIPE, stderr = STDOUT, shell = True, text=True)
    elif macOSVersion == "Catalina":
        macrec = Popen(MacRecoveryPath + " -b Mac-00BE6ED71E35EB86 -m 00000000000000000 download -n macOS-Catalina", stdout = PIPE, stderr = STDOUT, shell = True, text=True)
    elif macOSVersion == "Mojave":
        macrec = Popen(MacRecoveryPath + " -b Mac-7BA5B2DFE22DDD8C -m 00000000000KXPG00 download -n macOS-Mojave", stdout = PIPE, stderr = STDOUT, shell = True, text=True)
    else:
        con.send("Selected an unknown version of macOS".encode())
        return
    while True:
        line = macrec.stdout.readline()
        con.send(b"macrecovery: " + line.encode())
        if not line:
            con.send("Done downloading macOS\n".encode())
            if macOSVersion != "Big Sur":
                ConvertIMG(macOSVersion)
                MoveToProxISOFolder(macOSVersion)
            else:
                ConvertIMG("BigSur")
                MoveToProxISOFolder("BigSur")
            break


def WriteConfig(port, VMConfigLocation, macOSVersion):
    with open(VMConfigLocation, "a") as write_vmconfig:
        #ide0: local:iso/BigSur-recovery.img,cache=unsafe,size=2097012K
        print("I got here1")
        if macOSVersion != "Big Sur":
            Size = str((os.path.getsize('/var/lib/vz/template/iso/%s-recovery.img' % macOSVersion))/1024).strip(".0") + "K"
            write_vmconfig.write(port + ": local:iso/%s-recovery.img,cache=unsafe,size=%s\n" % (macOSVersion, Size))
            DebugWrite("\nAdded " + port + " for macOS %s recovery to vm config" % (macOSVersion))
        else:
            macOSVersion = "BigSur"
            Size = str((os.path.getsize('/var/lib/vz/template/iso/%s-recovery.img' % macOSVersion))/1024).strip(".0") + "K"
            write_vmconfig.write(port + ": local:iso/%s-recovery.img,cache=unsafe,size=%s\n" % (macOSVersion, Size))
            DebugWrite("\nAdded " + port + " for macOS %s recovery to vm config" % (macOSVersion))

def AddToVM(macOSVersion, vmid):
    macOSVersion = str(macOSVersion)
    vmid = str(vmid)
    con.send("Recieved request to add macOS ".encode() + macOSVersion.encode() + " to vm ".encode() + vmid.encode())
    DebugWrite("Got macOS version: " +  macOSVersion)
    DebugWrite("Got vm ID: " + vmid)

    VMConfigLocation = "/etc/pve/qemu-server/" + vmid + ".conf"
    DebugWrite("Chosen vm config location" + VMConfigLocation)

    with open (VMConfigLocation, 'r') as readconf:
        vmconfigcontents =  ("".join(line.strip() for line in readconf))
        AllSataAndIdePorts = ["ide0", "ide2", "sata0", "sata1", "sata2", "sata3", "sata4", "sata5", "sata6"]
        if all(x in vmconfigcontents for x in AllSataAndIdePorts):
            DebugWrite("All SATA ports from 1-5 and IDE ports 0 and 2 are used in the VM, please remove a used IDE or SATA port from the vm")
            exit()
        for port in AllSataAndIdePorts:
            if port not in vmconfigcontents:
                DebugWrite("Not in VM config: %s" % (port))
                WriteConfig(port, VMConfigLocation, macOSVersion)
                break

while True:
    try:
        DebugWrite("I'm true")
        DebugWrite("recieving")
        message = con.recv( 1024 ).decode()
        if not message: raise socket.error
        DebugWrite("recieved")
        DebugWrite(message)
        if 'download' in message:
            con.send(b"Request to download macOS recieved\n")
            DebugWrite("Got from Client: " + message)
            macversion = message.replace("download ", '')
            getmacOS(macversion)

        elif 'add' in (str(repr(message))):
            #add Monterey 104
            con.send(b"Request to add macOS recovery to vm recieved\n")
            DebugWrite("Got from Client: " + message)
            message = message.replace("add", "")
            messagewords = message.split()

            for index, word in enumerate(messagewords):
                if (index == 0): #Check index bounds
                    # Big Sur and High Sierra are 2 seperate words..
                    if str(messagewords[index+1]).isdigit():
                        macOSversion = str(word)
                        vmid = str(messagewords[index+1])
                    else:
                        macOSversion = str(word) + ' ' + str(messagewords[index+1])
                        vmid = str(messagewords[index+2])
                    AddToVM(macOSversion, vmid)

    except socket.error:
        DebugWrite("Error reading data. The connection is probably closed.")
        # set connection status and recreate socket
        connected = False
        con = socket.socket()
        DebugWrite("Connection lost... reconnecting")
        while not connected:
            try:
                DebugWrite("Reconnect stage 1.0")
                # create and configure socket on local host
                serverSocket = socket.socket()
                DebugWrite("Reconnect stage 1.1")
                serverSocket.bind((host, port))
                DebugWrite("Reconnect stage 1.2")
                serverSocket.listen(1)
                DebugWrite("Reconnect stage 1.3. Waiting for clients to connect")
                con, addr = serverSocket.accept()
                DebugWrite("Reconnect stage 2.0. Client connected.")
                serverSocket.listen(1)
                DebugWrite("Reconnect stage 2.1.")
                connected = True
                DebugWrite("Reconnect stage 2.2. Reconnect successful.")
            except:
                sleep(2)