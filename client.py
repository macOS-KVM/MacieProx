# Import Module
from tkinter import *
from tkinter import ttk
import socket, sys
from threading import *
from tkinter.messagebox import *
  
# Create Object
root = Tk()

root.title("MacieProx Client")  
# Set geometry
root.geometry("400x400")

fm1 = Frame(root)
fm2 = Frame(root)
fm3 = Frame(root)

# use threading
def threading():
    print("1 begin")
    # Call download function
    t1=Thread(target=Connect)
    print("1 start")
    t1.start()    
    print("1 started")

# use threading
def threading2():
    print("2 begin")
    # Call read function
    t2=Thread(target=read)
    print("2 start")
    t2.start()    
    print("2 started")

# use threading
def threading3():
    print("3 begin")
    # Call download function
    t3=Thread(target=startdownload)
    print("3 start")
    t3.start()    
    print("3 started")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connected = True  

def read():
    while True:  
        try:
            from_server = sock.recv(4096)
            if not from_server: 
                print("No data")
                break
            message = from_server.decode()
            textbox.insert(END, message)
            textbox.see("end") 
            if 'macrecovery: Done downloading macOS' in message:
                AddRecToVM(mycombo.get())
        except socket.error: 
            showerror("ERROR", "Connection lost!")   
            break

def startdownload():
    try:
        sock.send("download ".encode() + mycombo.get().encode())
        threading2()
    except socket.error:
        showerror("ERROR", "Connection lost!")

class Connect:
    def __init__(self):
        self.ConnecWindow = Toplevel(root)
        self.ConnecWindow.title("Connect")
        self.ConnecWindow.geometry("300x130")

        # Create the frames
        fm1ConnectWindow= Frame(self.ConnecWindow)
        fm2ConnectWindow = Frame(self.ConnecWindow)
        fm3ConnectWindow = Frame(self.ConnecWindow)

        # Create IP adress label
        Label(fm1ConnectWindow, text='IP address:').pack(side='left', expand=1)

        # Create IP address entry
        IP_Address = Entry(fm1ConnectWindow)
        IP_Address.pack(side='left', expand=1)

        # Create IP adress label
        Label(fm2ConnectWindow, text='Port:').pack(side='left', expand=1)

        # Create port entry
        port = Entry(fm2ConnectWindow)
        port.pack(side='left', expand=1)
        port.insert(0, "26")

        # connect button
        Button(fm3ConnectWindow, text="Connect", command=lambda: self.tryconnect(IP_Address.get(), port.get())).pack()

        # Pack the Frames
        fm1ConnectWindow.pack(pady=10)
        fm2ConnectWindow.pack(pady=10)
        fm3ConnectWindow.pack(pady=10)

    def tryconnect(self, IP_Address, port):
        try:
            # Connect the socket to the port where the server is listening
            print("connecting...")
            server_address = (IP_Address, int(port))
            print (sys.stderr, 'connecting to %s port %s' % server_address)
            sock.connect(server_address)
            self.ConnecWindow.destroy()
            showinfo("Connected", "Connected")
        except:
            showerror("ERROR", "Failed to connect.\nMake sure the IP adress and port are correct and the server is running.")

def on_closing(): # avoid script keeps running when tkinter window is closed
    sock.close()
    exit()

class AddRecToVM:
    def __init__(self, macOSversion):
        self.macOSversion = macOSversion
        print("Got macOS version:", self.macOSversion)
        addtovmconfig = askyesno("Add to vm?", "Do you want to add the macOS recovery you just downloaded to the VM config?")
        if addtovmconfig == True:
            self.window()

    def window(self):
        print("I'm at the new window")
        print("I got macOS version:", self.macOSversion)
        
        # sets the toplevel, title and geometry
        self.AddRecToVMWindow = Toplevel(root)
        self.AddRecToVMWindow.title("Add recovery to vm")
        self.AddRecToVMWindow.geometry("300x100")

        # Create the frames
        fm1AddRecToVMWindow = Frame(self.AddRecToVMWindow)
        fm2AddRecToVMWindow = Frame(self.AddRecToVMWindow)

        # Create vmid label
        Label(fm1AddRecToVMWindow, text='Enter the VM ID:').pack(side='left', expand=1)

        # Create vmid entry
        VmidEntry = Entry(fm1AddRecToVMWindow)
        VmidEntry.pack(side='left', expand=1)

        # Add to vm config button
        Button(fm2AddRecToVMWindow, text="Add macOS recovery to VM config", command=lambda: self.addtovm(VmidEntry.get())).pack()

        # Pack the Frames
        fm1AddRecToVMWindow.pack(pady=10)
        fm2AddRecToVMWindow.pack(pady=10)

    def addtovm(self, vmid):
        self.vmid = vmid
        if self.vmid == '':
            showerror("ERROR", "No VMID has been selected!")
        else:
            print("I got macOS version:", self.macOSversion)
            print("I got the following vmid:", self.vmid)
            print("I'm adding it to the vm")
            command = str("add " + self.macOSversion + " " + self.vmid)
            print("I'll send the following command:", command)
            try:  
                sock.send(command.encode())
                threading2()
                self.AddRecToVMWindow.destroy()
            except socket.error:
                showerror("ERROR", "Not Connected!")

# Gui buttons, etc
macOSOptions = ["Monterey", "Big Sur", "Catalina", "Mojave"]

# Connect Button
Button(fm1,text="connect",command = threading).pack()

# Select macOS version label
Label(fm2, text="Select macOS version:").pack(side='left', expand=1)

# macOS selection box
mycombo = ttk.Combobox(fm2, value=macOSOptions)
mycombo.current(0)
mycombo.pack(side='left', expand=1)

# Download Button
Button(fm2,text="download",command = threading3).pack(side='left', expand=1, padx=10)

# Textbox and scrollbar
scrollbar = Scrollbar(fm3)
scrollbar.pack(side=RIGHT, fill=Y)
textbox = Text(fm3)
textbox.pack()

# Attach textbox to scrollbar
textbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=textbox.yview)

root.protocol("WM_DELETE_WINDOW", on_closing)
  
# pack the frames
fm1.pack(pady=10)
fm2.pack(pady=10)
fm3.pack(pady=10)

# Execute Tkinter
root.mainloop()