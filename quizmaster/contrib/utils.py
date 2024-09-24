'''
Created on 20 avr. 2022

@author: denis
'''
from datetime import datetime
import string, secrets, random
import uuid, socket
from decimal import Decimal

random.seed()

def randint(start=0, stop=1000):
    return random.randint(start, stop)


def bitread(b, bitpos):
    return (b>>bitpos) & 0x1


def get_fqdn():
    return socket.getfqdn()


def get_uuid():
    return str(hex(uuid.getnode()))[2:]


def ts_now(m=1):
    now = datetime.now().timestamp()*m
    return int(now)


def random_chars(n=6):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(n))  # @UnusedVariable

def get_apikey(n=32):
    chars = 'abcdefghijklABCDEFGHIJKLmnopqrstuvwxyz0123456789MNOPQRSTUVWXYZ'
    return ''.join(secrets.choice(chars) for i in range(n))  # @UnusedVariable


def str_to_float(n, default='NaN'):
    try:
        return float(str(n).strip().replace(',', '.'))
    except:
        return default

def str_to_int(n, default='NaN'):
    try:
        return int(str(n).strip())
    except:
        return default

def gps_conv(s, n=1000000, default='NaN'):
    try:
        return str( int(Decimal(s)*n) )
    except:
        return default

def conv_gps(v, default=None):
    try:
        if v == 'NaN':
            raise
        return float(Decimal(v)/1000000)
    except:
        return default



