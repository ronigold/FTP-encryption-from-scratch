import socket
import os
import sys
from pip._vendor.distlib.compat import raw_input
from encoded import *

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
		while True:
			try:
				command = self.input_command()
			except KeyboardInterrupt:
				self.close_client()

			cmd  = command[:4].strip().upper()
			path = command[4:].strip()
			cwd = os.getcwd()
			fname = os.path.join(cwd, path)
			try:
				b = caesar_encode(command, self.step)
				self.sock.send(b)
				data = self.sock.recv(1024)
				data = caesar_decode(data, self.step)
				print (data)

				if (cmd == 'QUIT'):
					self.close_client()
				elif (cmd == 'LIST' or cmd == 'STOR' or cmd == 'RETR'):
					if (data and (data[0:3] == 'FYI')):
						func = getattr(self, cmd)
						func(path)
						data = self.sock.recv(1024)
						data = caesar_decode(data, self.step)
						print (data)
			except Exception as e:
				print (str(e))
				self.close_client()

	def input_command(self):
		command = raw_input('Enter command: ')
		if not command:
			print('Need a command.')

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
