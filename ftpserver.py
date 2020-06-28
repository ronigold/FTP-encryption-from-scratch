import socket
import threading
import pandas as pd
from random import randint
from pip._vendor.distlib.compat import raw_input
from server_func import *

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

class FTPThreadServer(threading.Thread):
	def __init__(self, client_client_address, local_ip, data_port):
		client, client_address = client_client_address
		self.client = client
		self.client_address = client_address
		self.username = 'Unknown'
		self.cwd = os.getcwd()
		self.data_address = (local_ip, data_port)
		self.step = randint(1,22)

		threading.Thread.__init__(self)

	def start_datasock(self):
		try:
			print('Creating data socket on' + str(self.data_address) + '...')

			self.datasock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.datasock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			self.datasock.bind(self.data_address)
			self.datasock.listen(5)

			print('Data socket is started. Listening to' + str(self.data_address) + '...')
			massage = 'FYI Data connection already open; transfer starting.\r\n'
			massage = caesar_encode(massage, self.step)
			self.client.send(massage)

			return self.datasock.accept()
		except Exception as e:
			print('ERROR: test ' + str(self.client_address) + ': ' + str(e))
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
		print(username, password, username_client, password_client, username_client in (username), password_client in (password))
		return (username_client in (username) and password_client in (password))

	def run(self):
		print('Login Request, client:' + str(self.client_address) + '\n')
		users = pd.read_excel('clients.xlsx')
		username = []
		password = []
		for i in range(len(users)):
			username.append(users.loc[i, 'username'])
			password.append(users.loc[i, 'password'])
		choice = self.client.recv(1024)
		choice = int(choice.decode('utf-8'))
		if choice == 2:
			self.step = DES_key()
			caesar_encode = DES_encode
			caesar_decode = DES_decode
		massage = str(self.step)
		massage = massage.encode('utf-8')
		self.client.send(massage)
		username_client, password_client = 'a', 'a'
		while not self.login(username, password, username_client, password_client):
			username_client = self.client.recv(1024)
			username_client = caesar_decode(username_client, self.step)
			password_client = self.client.recv(1024)
			password_client = caesar_decode(password_client, self.step)
			if self.login(username, password, username_client, password_client):
				self.username = username_client
				massage = 'Successfully connected!' + '\n'
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
				print('Commands from ' + str(self.client_address) + ': ' + cmd)
				try:
					func = getattr(self, cmd[:4].strip().upper())
					func(cmd)
				except AttributeError as e:
					print ('ERROR: ' + str(self.client_address) + ': Invalid Command.')
					massage = 'Invalid Command\r\n'
					massage = caesar_encode(massage, self.step)
					self.client.send(massage)
		except Exception as e:
			print ('ERROR: ' + str(self.client_address) + ': ' + str(e))
			self.QUIT('')

	def RETR(self, cmd):
		path = cmd[4:].strip()
		if not path:
			massage = 'Missing arguments <filename>.\r\n'
			massage = caesar_encode(massage, self.step)
			self.client.send(massage)
			return

		fname = os.path.join(self.cwd, path)
		(client_data, client_address) = self.start_datasock()
		if not os.path.isfile(fname):
			massage = 'File not found.\r\n'
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

				massage = 'Transfer complete.\r\n'
				massage = caesar_encode(massage, self.step)
				self.client.send(massage)
			except Exception as e:
				print('ERROR: ' + str(self.client_address) + ': ' + str(e))
				massage = 'Connection closed; transfer aborted.\r\n'
				massage = caesar_encode(massage, self.step)
				self.client.send(massage)
			finally:
				client_data.close()
				self.close_datasock()
				file_read.close()


	def SYST(self, cmd):
		massage = 'Server type: ' + platform.system() + '\r\n' + \
				  'Server name: ' + os.name + '\r\n' + \
				  'Server release: ' + platform.release() + '\r\n' + \
				  'Server machine: ' + platform.machine() + '\r\n' + \
				  'Server version: ' + platform.version() + '\r\n'

		massage = caesar_encode(massage, self.step)
		self.client.send(massage)


	def DSIZ(self, cmd):
		root_directory = Path('.')
		massage = 'Directory Size: ' + '\r\n' + \
				  str(sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file())) + ' (bytes)' + '\r\n' \
				  + str(sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file()) * 0.001) + ' KB' + '\r\n'

		massage = caesar_encode(massage, self.step)
		self.client.send(massage)


	def MDTM(self, cmd):
		path = cmd[4:].strip()
		if not path:
			massage = 'Missing arguments <filename>.\r\n'
			massage = caesar_encode(massage, self.step)
			self.client.send(massage)
			return

		(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(path)
		massage = "last modified: %s" % time.ctime(mtime)

		massage = caesar_encode(massage, self.step)
		self.client.send(massage)


	def QUIT(self, cmd):
		try:
			massage = 'Quit - client logout\r\n'
			massage = caesar_encode(massage, self.step)
			self.client.send(massage)
		except:
			pass
		finally:
			print('Closing connection from ' + str(self.client_address) + '...')
			self.close_datasock()
			self.client.close()
			quit()
class FTPserver:
	def __init__(self, port, data_port):
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


port = raw_input("Enter port: (if you left empty, default port is 10000)")
if not port:
	port = 10000

data_port = raw_input("Enter data port: (if you left empty, default port is 10001)")
if not data_port:
	data_port = 10001

server = FTPserver(port, data_port)
server.start()
