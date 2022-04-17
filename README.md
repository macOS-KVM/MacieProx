# Usage
## Server side (proxmox host)
- SSH to the Proxmox host OR use console of the Proxmox host on it's web interface
- Clone this repo and execute the script `git clone https://github.com/Core-i99/MacieProx.git && python3 MacieProx/server.py`
- The server.py script won't do anything until you connect to it with the client. If a firewall is configured then don't forget to open the port the script uses (26) otherwise you can't connect.


## Client side (any other pc in your network: macOS, Windows or anything which runs python)
- Clone the repository
- Run in terminal (macOS) or cmd (Windows): python3 client.py (of course, first cd into the directory where you saved client.py)
- The GUI will now open, you can connect to the server.

