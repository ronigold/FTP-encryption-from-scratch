import string
from Crypto.Cipher import DES
import re
import random

def caesar_encode(text, step, alphabets = (string.ascii_lowercase, string.ascii_uppercase, string.digits)):
    def shift(alphabet):
        return alphabet[step:] + alphabet[:step]

    shifted_alphabets = tuple(map(shift, alphabets))
    joined_aphabets = ''.join(alphabets)
    joined_shifted_alphabets = ''.join(shifted_alphabets)
    table = str.maketrans(joined_aphabets, joined_shifted_alphabets)
    text = text.translate(table); print('Send encode message (Caesars Method)', text)
    return text.encode('utf-8')

def caesar_decode(text, step, alphabets = (string.ascii_lowercase, string.ascii_uppercase, string.digits)):
    def shift(alphabet):
        return alphabet[step:] + alphabet[:step]
    step = -step;
    text = text.decode('utf-8'); print(text)
    shifted_alphabets = tuple(map(shift, alphabets))
    joined_aphabets = ''.join(alphabets)
    joined_shifted_alphabets = ''.join(shifted_alphabets)
    table = str.maketrans(joined_aphabets, joined_shifted_alphabets)
    text = text.translate(table)
    return text


def DES_key(stringLength=8):
	letters = string.ascii_lowercase
	key = ''.join(random.choice(letters) for i in range(stringLength))
	return str.encode(key)


def DES_encode(text, key):
	cipher = DES.new(key, DES.MODE_CBC)
	if len(text) % 8 != 0:
		toAdd = 8 - len(text) % 8
		text += ' '*toAdd
	text = str.encode(text)
	return cipher.encrypt(text)

def DES_decode(text, key):
    cipher = DES.new(key, DES.MODE_CBC)
    text = cipher.decrypt(text).decode("utf-8")
    return re.sub("^\s+|\s+$", "", text, flags=re.UNICODE)
