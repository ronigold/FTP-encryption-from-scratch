import socket
import os
import sys
from pip._vendor.distlib.compat import raw_input
from encryption import *

class FTPclient:
	def __init__(self, address, port, data_port):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.address = address
		self.port = int(port)
		self.data_port = int(data_port)
		self.encryption = 1
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
		while True:
			encryption = raw_input('Select the type of encryption you want:' + '\n' + '[1] Caesar' + '\n' + '[2] DES' + '\n' )
			if encryption != '1' and encryption != '2':
				print('Please enter a valid value only. Try again')
			else:
				break
		print('Sending server login request ...')
		self.encryption = encryption
		encryption = str(encryption)
		encryption = encryption.encode('utf-8')
		self.sock.send(encryption)
		step = self.sock.recv(1024)
		step = step.decode('utf-8')
		encryption = int(encryption)
		if encryption == 1:
			step = int(step)
		self.step = step
		print('Key recv from server to caesar encode:', self.step)
		while True:
			username = raw_input('Enter username: ')
			password = raw_input('Enter password: ')
			username = encode(self.encryption, username, self.step)
			self.sock.send(username)
			password = encode(self.encryption, password, self.step)
			self.sock.send(password)
			data = self.sock.recv(1024)
			data = decode(self.encryption, data, self.step)
			print(data)
			if data == 'Successfully connected!' + '\n':
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
				print('Missing arguments <filename>.\r\n')
				continue
			if cmd == 'STOR' and not os.path.isfile(fname):
				print('File not found.\r\n')
				continue
			if cmd == 'MDTM' and not os.path.isfile(fname):
				print('File not found.\r\n')
				continue
			try:
				b = encode(self.encryption, command, self.step)
				self.sock.send(b)
				data = self.sock.recv(1024)
				data = decode(self.encryption, data, self.step)
				print (data)

				if (cmd == 'QUIT'):
					self.close_client()
				elif (cmd == 'LIST' or cmd == 'STOR' or cmd == 'RETR'):
					if (data and (data[0:3] == 'FYI')):
						func = getattr(self, cmd)
						func(path)
						data = self.sock.recv(1024)
						data = decode(self.encryption, data, self.step)
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
				dirlist = decode(self.encryption, dirlist, self.step)
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
				upload = encode(self.encryption, upload, self.step)
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

				download = decode(self.encryption, download, self.step)
				f.write(download)
		except Exception as e:
			print (str(e))
		finally:
			f.close()
			self.datasock.close()

	def close_client(self):

		print ('Closing socket connection...')
		self.sock.close()
		print ('FTP client terminating...')
		quit()


address = raw_input("Enter destination address: (if you left empty, default address is localhost) ")
if not address:
	address = 'localhost'

port = raw_input("Enter port: (if you left empty, default port is 10000) ")
if not port:
	port = 10000

data_port = raw_input("Enter data port: (if you left empty, default port is 10001)")
if not data_port:
	data_port = 10001

ftpClient = FTPclient(address, port, data_port)
ftpClient.start()
