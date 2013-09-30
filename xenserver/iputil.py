# IP utilities library

import socket
import struct


def iptos(ipl):
    return socket.inet_ntoa(struct.pack('!L', ipl))

def ipcalc(subnet):
    b = subnet.strip().split('/')
    ip = b[0]
    cidr = int(b[1])

    ipnl = struct.unpack('!L', socket.inet_aton(ip))[0]

    first = ipnl + 1

    last = ipnl + (2**(32-cidr) - 2)

    return ipnl, first, last, cidr

def expandSubnet(subnet):
    ipnl, first, last, cidr = ipcalc(subnet)

    second = first + 1

    iplist = [iptos(i) for i in range(second, last+1)]
    return iplist

def firstRemaining(subnet, used):
    ips = list(set(expandSubnet(subnet)).difference(used))
    ips.sort()
    return ips[0]

def allRemaining(subnet, used):
    ips = list(set(expandSubnet(subnet)).difference(used))
    ips.sort()
    return ips

def getGateway(subnet):
    ipnl, first, last, cidr = ipcalc(subnet)

    return iptos(first)


