import string
from des import DesKey
import random

def encode(encryption, text, step):
    encryption = int(encryption)
    if encryption == 1:
        step = int(step)
        return caesar_encode(text, step, alphabets = (string.ascii_lowercase, string.ascii_uppercase, string.digits))
    else:
        return DES_encode(text, step)

def decode(encryption, text, step):
    encryption = int(encryption)
    if encryption == 1:
        step = int(step)
        return caesar_decode(text, step, alphabets = (string.ascii_lowercase, string.ascii_uppercase, string.digits))
    else:
        return DES_decode(text, step)

def caesar_encode(text, step, alphabets = (string.ascii_lowercase, string.ascii_uppercase, string.digits), mode=0):
    def shift(alphabet):
        return alphabet[step:] + alphabet[:step]

    shifted_alphabets = tuple(map(shift, alphabets))
    joined_aphabets = ''.join(alphabets)
    joined_shifted_alphabets = ''.join(shifted_alphabets)
    table = str.maketrans(joined_aphabets, joined_shifted_alphabets)
    if mode == 1:
        return text.translate(table)
    text = text.translate(table); print('Send encode message (Caesars Method)', text)
    return text.encode('utf-8')

def caesar_decode(text, step, alphabets = (string.ascii_lowercase, string.ascii_uppercase, string.digits), mode=0):
    def shift(alphabet):
        return alphabet[step:] + alphabet[:step]
    step = -step;
    if mode == 0:
        text = text.decode('utf-8')
    shifted_alphabets = tuple(map(shift, alphabets))
    joined_aphabets = ''.join(alphabets)
    joined_shifted_alphabets = ''.join(shifted_alphabets)
    table = str.maketrans(joined_aphabets, joined_shifted_alphabets)
    text = text.translate(table)
    return text

def encryption_key(encryption):
    if encryption == 1:
        return random.randint(1,22), 'Caesar'
    else:
        return DES_key(), 'DES'

def DES_key():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(16))


def DES_encode(text, key):
    key = str.encode(key)
    key_des = DesKey(key)
    data = text.encode('utf-8')
    print('Send encode message (DES)', key_des.encrypt(data, padding=True))
    return key_des.encrypt(data, padding = True)

def DES_decode(text, key):
    key = str.encode(key)
    key_des = DesKey(key)
    data = key_des.decrypt(text, padding=True)
    return data.decode('utf-8')