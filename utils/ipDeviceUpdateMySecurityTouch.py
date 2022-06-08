from subprocess import Popen, PIPE
from time import sleep

import requests

url = 'http://localhost:1234'

def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output.decode('ascii')

def find_interface():
    find_device = "ip addr show"
    interface_parse = run_cmd(find_device)
    for line in interface_parse.splitlines():
        if "state UP" in line:
            dev_name = line.split(':')[1]
    return dev_name

def parse_ip(activeInterface):
    find_ip = "ip addr show %s" % activeInterface
    find_ip = "ip addr show %s" % activeInterface
    ip_parse = run_cmd(find_ip)
    for line in ip_parse.splitlines():
        if "inet " in line:
            ip = line.split(' ')[5]
            ip = ip.split('/')[0]
    return ip

def ipCheck(ipCurrent=None):
    try:
        endPoint = url + '/ipUtils/guardarIpCurrent'
        data={"ipCurrent":ipCurrent}
        response = requests.post(endPoint,data=data)
        return response.get_json()
    except:
        print('No se logro llamar al servidor backend')

while True:
    ipCheck(parse_ip(find_interface()))
    sleep(43200)