from cryptography.fernet import Fernet
from config import get_cfg

key = str.encode(get_cfg('dec')['key'])


def encr(data):
    return Fernet(key).encrypt(data.encode('UTF-8')).decode('UTF-8')


def decr(data):
    return Fernet(key).decrypt(data.encode('UTF-8')).decode('UTF-8')
