# simple FTP client
# commands
#		LIST <path>, information of a directory or file,
#					 or information of current remote directory if not specified
#		STOR <file_name>, copy file to current remote directory 
# 	RETR <file_name>, retrieve file from current remote directory
# additional commands
#		PWD, get current remote directory
#		CDUP, change to parent remote directory
#		CWD <path>, change current remote directory
#		MKD, make a directory in remote server
#		RMD <dir_name>, remove a directory in remote server
#		DELE <file_name>, delete a file in remote server 

import socket
import os
import sys
import string
from pip._vendor.distlib.compat import raw_input

def caesar_encode(text, step, alphabets = (string.ascii_lowercase, string.ascii_uppercase, string.digits)):

    def shift(alphabet):
        return alphabet[step:] + alphabet[:step]

    shifted_alphabets = tuple(map(shift, alphabets))
    joined_aphabets = ''.join(alphabets)
    joined_shifted_alphabets = ''.join(shifted_alphabets)
    table = str.maketrans(joined_aphabets, joined_shifted_alphabets)
    text = text.translate(table); print('send encode message to client(Caesars Method)', text)
    return text.encode('utf-8')

def caesar_decode(text, step, alphabets = (string.ascii_lowercase, string.ascii_uppercase, string.digits)):

    def shift(alphabet):
        return alphabet[step:] + alphabet[:step]
    step = -step
    text = text.decode('utf-8')
    shifted_alphabets = tuple(map(shift, alphabets))
    joined_aphabets = ''.join(alphabets)
    joined_shifted_alphabets = ''.join(shifted_alphabets)
    table = str.maketrans(joined_aphabets, joined_shifted_alphabets)
    text = text.translate(table)
    return text

class FTPclient:
	def __init__(self, address, port, data_port):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.address = address
		self.port = int(port)
		self.data_port = int(data_port)
		self.step = 1

	def create_connection(self):
	  print ('Starting connection to', self.address, ':', self.port)

	  try:
	  	server_address = (self.address, self.port)
	  	self.sock.connect(server_address)
	  	print ('Connected to', self.address, ':', self.port)
	  except KeyboardInterrupt:
	  	self.close_client()
	  except:
	  	print ('Connection to', self.address, ':', self.port, 'failed')
	  	self.close_client()

	def start(self):
		try:
			self.create_connection()
		except Exception as e:
			self.close_client()
		print('Sending server login request ...')
		step = self.sock.recv(1024)
		step = step.decode('utf-8')
		step = int(step)
		self.step = step
		print('Key recv from server to caesar encode:', self.step)
		while True:
			username = raw_input('Enter username: ')
			password = raw_input('Enter password: ')
			username = caesar_encode(username, self.step)
			self.sock.send(username)
			password = caesar_encode(password, self.step)
			self.sock.send(password)
			data = self.sock.recv(1024)
			data = caesar_decode(data, self.step)
			print(data)
			if data == 'successfully connected!' + '\n':
				break
		while True:
			try:
				command = raw_input('Enter command: ')
				if not command: 
					print ('Need a command.')
					continue
			except KeyboardInterrupt:
				self.close_client()

			cmd  = command[:4].strip().upper()
			path = command[4:].strip()
			cwd = os.getcwd()
			fname = os.path.join(cwd, path)
			if cmd == 'STOR' and not path:
				print('501 Missing arguments <filename>.\r\n')
				continue
			if cmd == 'STOR' and not os.path.isfile(fname):
				print('550 File not found.\r\n')
				continue
			try:
				b = caesar_encode(command, self.step)
				self.sock.send(b)
				data = self.sock.recv(1024)
				data = caesar_decode(data, self.step)
				print (data)

				if (cmd == 'QUIT'):
					self.close_client()
				elif (cmd == 'LIST' or cmd == 'STOR' or cmd == 'RETR'):
					if (data and (data[0:3] == '125')):
						func = getattr(self, cmd)
						func(path)
						data = self.sock.recv(1024)
						data = caesar_decode(data, self.step)
						print (data)
			except Exception as e:
				print (str(e))
				self.close_client()

	def connect_datasock(self):
		self.datasock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.datasock.connect((self.address, self.data_port))

	def LIST(self, path):
		try:
			self.connect_datasock()

			while True:
				dirlist = self.datasock.recv(1024)
				dirlist = caesar_decode(dirlist, self.step)
				if not dirlist: break
				sys.stdout.write(dirlist)
				sys.stdout.flush()
		except Exception as e:
			print (str(e))
		finally:
			self.datasock.close()

	def STOR(self, path):
		print ('Storing', path, 'to the server')
		try:
			self.connect_datasock()

			f = open(path, 'r')
			upload = f.read(1024)
			while upload:
				upload = caesar_encode(upload, self.step)
				self.datasock.send(upload)
				upload = f.read(1024)
		except Exception as e:
			print (str(e))
		finally:
			f.close()
			self.datasock.close()

	def RETR(self, path):
		print ('Retrieving', path, 'from the server')
		try:
			self.connect_datasock()

			f = open(path,'w')
			while True:
				download = self.datasock.recv(1024)
				if not download:
					break

				download = caesar_decode(download, self.step)
				f.write(download)
		except Exception as e:
			print (str(e))
		finally:
			f.close()
			self.datasock.close()

	# stop FTP client, close the connection and exit the program
	def close_client(self):
		print ('Closing socket connection...')
		self.sock.close()

		print ('FTP client terminating...')
		quit()


address = raw_input("Destination address - if left empty, default address is localhost: ")

if not address:
	address = 'localhost'

port = raw_input("Port - if left empty, default port is 10021: ")

if not port:
	port = 10021

data_port = raw_input("Data port - if left empty, default port is 10020: ")

if not data_port:
	data_port = 10020

ftpClient = FTPclient(address, port, data_port)
ftpClient.start()