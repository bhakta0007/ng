Quick Dirty script to setup port forwarding and DHCP pinning on netgear router


# How to use

1. Create a virtual environment and set it up (one time)

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


2. Activate the env

source venv/bin/activate

3. Edit ng.py to match your env

you will see the below comments in ng.py as well
# To run this, you need to modify couple of thigns
# 1. Setup the path to firefox (replace what I have with your path)
# 2. Replace 192.168.31.1 with ip address of your netgear router
# 3. replace password with the base64 (echo "myRouterAdminPassword" | base64). Set this in password variable

4. Run

python ng.py
