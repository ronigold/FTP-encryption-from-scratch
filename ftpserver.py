# simple FTP server
# use multi-threading so it can handle multi FTP request
# commands
#   LIST <path>, information of a directory or file,
#   						 or information of current remote directory if not specified
#   STOR <file_name>, copy file to current remote directory 
#   RETR <file_name>, retrieve file from current remote directory
# additional commands
#	QUIT, quit connection
#	PWD, get current remote directory
#   CDUP, change to parent remote directory
#   CWD <path>, change current remote directory
#   MKD, make a directory in remote server
#   RMD <dir_name>, remove a directory in remote server
#   DELE <file_name>, delete a file in remote server 

import socket
import os
import sys
import threading
import time
import platform
import string
from random import randint

from pip._vendor.distlib.compat import raw_input

def caesar_encode(text, step, alphabets = (string.ascii_lowercase, string.ascii_uppercase, string.digits)):

    def shift(alphabet):
        return alphabet[step:] + alphabet[:step]

    shifted_alphabets = tuple(map(shift, alphabets))
    joined_aphabets = ''.join(alphabets)
    joined_shifted_alphabets = ''.join(shifted_alphabets)
    table = str.maketrans(joined_aphabets, joined_shifted_alphabets)
    text = text.translate(table); print('send encode message to server(Caesars Method)', text)
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

class FTPThreadServer(threading.Thread):
	def __init__(self, client_client_address, local_ip, data_port):
		client, client_address = client_client_address
		self.client = client
		self.client_address = client_address
		self.cwd = os.getcwd()
		self.data_address = (local_ip, data_port)
		self.step = randint(1,22)

		threading.Thread.__init__(self)

	def start_datasock(self):
		try:
			print ('Creating data socket on' + str(self.data_address) + '...')
			
			# create TCP for data socket
			self.datasock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.datasock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			self.datasock.bind(self.data_address)
			self.datasock.listen(5)
			
			print ('Data socket is started. Listening to' + str(self.data_address) + '...')
			massage = '125 Data connection already open; transfer starting.\r\n'
			massage = caesar_encode(massage, self.step)
			self.client.send(massage)

			return self.datasock.accept()
		except Exception as e:
			print ('ERROR: test ' + str(self.client_address) + ': ' + str(e))
			self.close_datasock()
			massage = '425 Cannot open data connection.\r\n'
			massage = caesar_encode(massage, self.step)
			self.client.send(massage)
			
	def close_datasock(self):
		print ('Closing data socket connection...')
		try:
			self.datasock.close()
		except:
			pass

	def login(self, username, password, username_client, password_client):
		return (username == username_client and password == password_client)

	def run(self):
		print('Login Request, client:' + str(self.client_address) + '\n')
		massage = str(self.step)
		massage = massage.encode('utf-8')
		self.client.send(massage)
		username_client, password_client = 'a', 'a'
		username, password = 'roni', 'gold'
		while not self.login(username, password, username_client, password_client):
			username_client = self.client.recv(1024)
			username_client = caesar_decode(username_client, self.step)
			password_client = self.client.recv(1024)
			password_client = caesar_decode(password_client, self.step)
			if self.login(username, password, username_client, password_client):
				massage = 'successfully connected!' + '\n'
				massage = caesar_encode(massage, self.step)
				self.client.send(massage)
			else:
				print('incorrect!. login_client:', username_client, password_client)
				print('login:', username, password)

				massage = 'Username or password incorrect. try again.' + '\n'
				massage = caesar_encode(massage, self.step)
				self.client.send(massage)
		try :
			print ('client connected: ' + str(self.client_address) + '\n')

			while True:
				cmd = self.client.recv(1024)
				cmd = caesar_decode(cmd, self.step)
				if not cmd: break
				print('commands from ' + str(self.client_address) + ': ' + cmd)
				try:
					func = getattr(self, cmd[:4].strip().upper())
					func(cmd)
				except AttributeError as e:
					print ('ERROR: ' + str(self.client_address) + ': Invalid Command.')
					massage = '550 Invalid Command\r\n'
					massage = caesar_encode(massage, self.step)
					self.client.send(massage)
		except Exception as e:
			print ('ERROR: ' + str(self.client_address) + ': ' + str(e))
			self.QUIT('')

	def QUIT(self, cmd):
		try:
			massage = '221 Goodbye.\r\n'
			massage = caesar_encode(massage, self.step)
			self.client.send(massage)
		except:
			pass
		finally:
			print ('Closing connection from ' + str(self.client_address) + '...')
			self.close_datasock()
			self.client.close()
			quit()

	def LIST(self, cmd):
		print ('LIST', self.cwd)
		(client_data, client_address) = self.start_datasock()

		try:
			listdir = os.listdir(self.cwd)
			if not len(listdir):
				max_length = 0
			else:
				max_length = len(max(listdir, key=len))

			header = '| %*s | %9s | %12s | %20s | %11s | %12s |' % (max_length, 'Name', 'Filetype', 'Filesize', 'Last Modified', 'Permission', 'User/Group')
			table = '%s\n%s\n%s\n' % ('-' * len(header), header, '-' * len(header))
			massage = caesar_encode(table, self.step)
			client_data.send(massage)

			for i in listdir:
				path = os.path.join(self.cwd, i)
				stat = os.stat(path)
				data = '| %*s | %9s | %12s | %20s | %11s | %12s |\n' % (max_length, i, 'Directory' if os.path.isdir(path) else 'File', str(stat.st_size) + 'B', time.strftime('%b %d, %Y %H:%M', time.localtime(stat.st_mtime))
					, oct(stat.st_mode)[-4:], str(stat.st_uid) + '/' + str(stat.st_gid))
				massage = caesar_encode(data, self.step)
				client_data.send(massage)

			table = '%s\n' % ('-' * len(header))
			massage = caesar_encode(table, self.step)
			client_data.send(massage)

			massage = '\r\n226 Directory send OK.\r\n'
			massage = caesar_encode(massage, self.step)
			self.client.send(massage)
		except Exception as e:
			print ('ERROR: ' + str(self.client_address) + ': ' + str(e))
			massage = '426 Connection closed; transfer aborted.\r\n'
			massage = caesar_encode(massage, self.step)
			self.client.send(massage)
		finally:
			client_data.close()
			self.close_datasock()

	def PWD(self, cmd):
		massage = '257 \"%s\".\r\n' % self.cwd
		massage = caesar_encode(massage, self.step)
		self.client.send(massage)

	def CWD(self, cmd):
		dest = os.path.join(self.cwd, cmd[4:].strip())
		if (os.path.isdir(dest)):
			self.cwd = dest
			massage = '250 OK \"%s\".\r\n' % self.cwd
			massage = caesar_encode(massage, self.step)
			self.client.send(massage)
		else:
			print ('ERROR: ' + str(self.client_address) + ': No such file or directory.')
			massage = '550 \"' + dest + '\": No such file or directory.\r\n'
			massage = caesar_encode(massage, self.step)
			self.client.send(massage)

	def CDUP(self, cmd):
		dest = os.path.abspath(os.path.join(self.cwd, '..'))
		if (os.path.isdir(dest)):
			self.cwd = dest
			massage = '250 OK \"%s\".\r\n' % self.cwd
			massage = caesar_encode(massage, self.step)
			self.client.send(massage)
		else:
			print ('ERROR: ' + str(self.client_address) + ': No such file or directory.')
			massage = '550 \"' + dest + '\": No such file or directory.\r\n'
			massage = caesar_encode(massage, self.step)
			self.client.send(massage)

	def MKD(self, cmd):
		path = cmd[4:].strip()
		dirname = os.path.join(self.cwd, path)
		try:
			if not path:
				massage = '501 Missing arguments <dirname>.\r\n'
				massage = caesar_encode(massage, self.step)
				self.client.send(massage)
			else:
				os.mkdir(dirname)
				massage = '250 Directory created: ' + dirname + '.\r\n'
				massage = caesar_encode(massage, self.step)
				self.client.send(massage)
		except Exception as e:
			print ('ERROR: ' + str(self.client_address) + ': ' + str(e))
			massage = '550 Failed to create directory ' + dirname + '.'
			massage = caesar_encode(massage, self.step)
			self.client.send('550 Failed to create directory ' + dirname + '.')

	def RMD(self, cmd):
		path = cmd[4:].strip()
		dirname = os.path.join(self.cwd, path)
		try:
			if not path:
				massage = '501 Missing arguments <dirname>.\r\n'
				massage = caesar_encode(massage, self.step)
				self.client.send(massage)
			else:
				os.rmdir(dirname)
				massage = '250 Directory deleted: ' + dirname + '.\r\n'
				massage = caesar_encode(massage, self.step)
				self.client.send(massage)
		except Exception as e:
			print ('ERROR: ' + str(self.client_address) + ': ' + str(e))
			massage = '550 Failed to delete directory ' + dirname + '.'
			massage = caesar_encode(massage, self.step)
			self.client.send(massage)

	def DELE(self, cmd):
		path = cmd[4:].strip()
		filename = os.path.join(self.cwd, path)
		try:
			if not path:
				massage = '501 Missing arguments <filename>.\r\n'
				massage = caesar_encode(massage, self.step)
				self.client.send(massage)
			else:
				os.remove(filename)
				massage = '250 File deleted: ' + filename + '.\r\n'
				massage = caesar_encode(massage, self.step)
				self.client.send(massage)
		except Exception as e:
			print ('ERROR: ' + str(self.client_address) + ': ' + str(e))
			massage = '550 Failed to delete file ' + filename + '.'
			massage = caesar_encode(massage, self.step)
			self.client.send(massage)

	def STOR(self, cmd):
		path = cmd[4:].strip()
		if not path:
			massage = '501 Missing arguments <filename>.\r\n'
			massage = caesar_encode(massage, self.step)
			self.client.send(massage)
			return

		fname = os.path.join(self.cwd, path)
		(client_data, client_address) = self.start_datasock()

		try:
			file_write = open(fname, 'w')
			while True:
				data = client_data.recv(1024)
				data = caesar_decode(data, self.step)
				if not data:
					break
				file_write.write(data)

			massage = '226 Transfer complete.\r\n'
			massage = caesar_encode(massage, self.step)
			self.client.send(massage)
		except Exception as e:
			print ('ERROR: ' + str(self.client_address) + ': ' + str(e))
			massage = '425 Error writing file.\r\n'
			massage = caesar_encode(massage, self.step)
			self.client.send(massage)
		finally:
			client_data.close()
			self.close_datasock()
			file_write.close()

	def RETR(self, cmd):
		path = cmd[4:].strip()
		if not path:
			massage = '501 Missing arguments <filename>.\r\n'
			massage = caesar_encode(massage, self.step)
			self.client.send(massage)
			return

		fname = os.path.join(self.cwd, path)
		(client_data, client_address) = self.start_datasock()
		if not os.path.isfile(fname):
			massage = '550 File not found.\r\n'
			massage = caesar_encode(massage, self.step)
			self.client.send(massage)
		else:
			try:
				file_read = open(fname, "r")
				data = file_read.read(1024)

				while data:
					data = caesar_encode(data, self.step)
					client_data.send(data)
					data = file_read.read(1024)

				massage = '226 Transfer complete.\r\n'
				massage = caesar_encode(massage, self.step)
				self.client.send(massage)
			except Exception as e:
				print ('ERROR: ' + str(self.client_address) + ': ' + str(e))
				massage = '426 Connection closed; transfer aborted.\r\n'
				massage = caesar_encode(massage, self.step)
				self.client.send(massage)
			finally:
				client_data.close()
				self.close_datasock()
				file_read.close()

	def SYST(self, cmd):
		print('heare')
		massage = 'Server type: ' + platform.system() + '\r\n' +\
				  'Server name: ' + os.name + '\r\n' +\
				  'Server release: ' + platform.release() + '\r\n' +\
				  'Server machine: ' + platform.machine() + '\r\n'  + \
				  'Server version: ' + platform.version() + '\r\n'

		massage = caesar_encode(massage, self.step)
		self.client.send(massage)

class FTPserver:
	def __init__(self, port, data_port):
		# server address at localhost
		self.address = '0.0.0.0'

		self.port = int(port)
		self.data_port = int(data_port)

	def start_sock(self):
		# create TCP socket
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_address = (self.address, self.port)

		try:
			print ('Creating data socket on', self.address, ':', self.port, '...')
			self.sock.bind(server_address)
			self.sock.listen(5)
			print ('Server is up. Listening to', self.address, ':', self.port)
		except Exception as e:
			print ('Failed to create server on', self.address, ':', self.port, 'because', str(e.strerror))
			quit()

	def start(self):
		self.start_sock()

		try:
			while True:
				print ('Waiting for a connection...')
				thread = FTPThreadServer(self.sock.accept(), self.address, self.data_port)
				thread.daemon = True
				thread.start()
		except KeyboardInterrupt:
			print ('Closing socket connection')
			self.sock.close()
			quit()


# Main
port = raw_input("Port - if left empty, default port is 10021: ")
if not port:
	port = 10021

data_port = raw_input("Data port - if left empty, default port is 10020: ")
if not data_port:
	data_port = 10020

server = FTPserver(port, data_port)
server.start()