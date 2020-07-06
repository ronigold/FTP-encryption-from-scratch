import socket
import os
import shutil
import threading
import time
import platform
import pandas as pd
from pathlib import Path
from pip._vendor.distlib.compat import raw_input
from encryption import *

class FTPThreadServer(threading.Thread):

    def __init__(self, client_client_address, local_ip, data_port):
        client, client_address = client_client_address
        self.client = client
        self.client_address = client_address
        self.username = 'Unknown'
        self.cwd = os.getcwd()
        self.data_address = (local_ip, data_port)
        self.encryption_type = 'Unknown'
        self.encryption = 1
        self.step = 1

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
            massage = encode(self.encryption, massage, self.step)
            self.client.send(massage)

            return self.datasock.accept()
        except Exception as e:
            print('ERROR: test ' + str(self.client_address) + ': ' + str(e))
            self.close_datasock()
            massage = '425 Cannot open data connection.\r\n'
            massage = encode(self.encryption, massage, self.step)
            self.client.send(massage)

    def close_datasock(self):

        print('Closing data socket connection...')
        try:
            self.datasock.close()
        except:
            pass

    def login(self, username, password, username_client, password_client):
        return (username_client in (username) and password_client in (password))

    def run(self):
        key_db = 18
        users = pd.read_excel('clients.xlsx')
        print(users)
        username = []
        password = []
        for i in range(len(users)):
            username.append(caesar_decode(users.loc[i, 'username'], key_db, mode = 1))
            password.append(caesar_decode(users.loc[i, 'password'], key_db, mode = 1))

        print(username, password)

        encryption = self.client.recv(1024)
        encryption = encryption.decode('utf-8')
        encryption = int(encryption)
        self.encryption = encryption
        self.step, self.encryption_type = encryption_key(encryption)
        print('Login Request, client: ' + str(self.client_address) + '\n' + 'Encryption: ' + self.encryption_type + '\n' )
        massage = str(self.step)
        massage = massage.encode('utf-8')
        self.client.send(massage)
        username_client, password_client = 'a', 'a'
        while not self.login(username, password, username_client, password_client):
            username_client = self.client.recv(1024)
            username_client = decode(self.encryption, username_client, self.step)
            password_client = self.client.recv(1024)
            password_client = decode(self.encryption, password_client, self.step)
            if self.login(username, password, username_client, password_client):
                self.username = username_client
                massage = 'Successfully connected!' + '\n'
                massage = encode(self.encryption, massage, self.step)
                self.client.send(massage)
            else:
                print('incorrect!. login_client:', username_client, password_client)

                massage = 'Username or password incorrect. try again.' + '\n'
                massage = encode(self.encryption, massage, self.step)
                self.client.send(massage)
            print('client connected: ' + str(self.client_address) + '\n')

        while True:
            cmd = self.client.recv(1024)
            cmd = decode(self.encryption, cmd, self.step)
            if not cmd: break
            print('Commands from ' + str(self.client_address) + ': ' + cmd)
            try:
                func = getattr(self, cmd[:4].strip().upper())
                func(cmd)
            except AttributeError as e:
                print('ERROR: ' + str(self.client_address) + ': Invalid Command.')
                massage = 'Invalid Command\r\n'
                massage = encode(self.encryption, massage, self.step)
                self.client.send(massage)

    def ACCT(self, cmd):

        massage = '------- Account information -------' + '\r\n' + \
                  'You are login in as:  ' + self.username + '\r\n' + \
                  'Your address is:  ' + str(self.client_address) + '\r\n'

        massage = encode(self.encryption, massage, self.step)
        self.client.send(massage)

    def LIST(self, cmd):

        print('LIST', self.cwd)
        (client_data, client_address) = self.start_datasock()
        print(client_data, client_address)

        try:
            listdir = os.listdir(self.cwd)
            if not len(listdir):
                max_length = 0
            else:
                max_length = len(max(listdir, key=len))

            header = '| %*s | %9s | %12s | %20s | %11s | %12s |' % (
            max_length, 'Name', 'Filetype', 'Filesize', 'Last Modified', 'Permission', 'User/Group')
            table = '%s\n%s\n%s\n' % ('-' * len(header), header, '-' * len(header))
            massage = encode(self.encryption, table, self.step)
            client_data.send(massage)

            for i in listdir:
                path = os.path.join(self.cwd, i)
                stat = os.stat(path)
                data = '| %*s | %9s | %12s | %20s | %11s | %12s |\n' % (
                max_length, i, 'Directory' if os.path.isdir(path) else 'File', str(stat.st_size) + 'B',
                time.strftime('%b %d, %Y %H:%M', time.localtime(stat.st_mtime))
                , oct(stat.st_mode)[-4:], str(stat.st_uid) + '/' + str(stat.st_gid))
                massage = encode(self.encryption, data, self.step)
                client_data.send(massage)

            table = '%s\n' % ('-' * len(header))
            massage = encode(self.encryption, table, self.step)
            client_data.send(massage)

            massage = '\r\nDirectory send OK.\r\n'
            massage = encode(self.encryption, massage, self.step)
            self.client.send(massage)

        except Exception as e:
            print('ERROR: ' + str(self.client_address) + ': ' + str(e))
            massage = 'Connection closed; transfer aborted.\r\n'
            massage = encode(self.encryption, massage, self.step)
            self.client.send(massage)
        finally:
            client_data.close()
            self.close_datasock()

    def PWD(self, cmd):

        massage = '\"%s\".\r\n' % self.cwd
        massage = encode(self.encryption, massage, self.step)
        self.client.send(massage)

    def FEAT(self, cmd):

        massage = '------------------------------   feature list implemented by the server   ------------------------------' + '\r\n' + \
                  '1. `ACCT` - Account information' + '\r\n' + \
                  '2. `LIST` - information of a directory or file or information of current remote directory if not specified' + '\r\n' + \
                  '3. `STOR <file_name>` - copy file to current remote directory' + '\r\n' + \
                  '4. `RETR <file_name>` - retrieve file from current remote directory' + '\r\n' + \
                  '5. `AVBL` - Get the available space on server' + '\r\n' + \
                  '6. `DSIZ` - Get the directory size' + '\r\n' + \
                  '7. `PWD` - get current remote directory' + '\r\n' + \
                  '8. `CDUP` - change to parent remote directory' + '\r\n' + \
                  '9. `CWD <path>` - change current remote directory' + '\r\n' + \
                  '10. `MKD <dir_name>` - make a directory in remote server' + '\r\n' + \
                  '11. `RMD <dir_name>` - remove a directory in remote server' + '\r\n' + \
                  '12. `DELE <file_name>` - delete a file in remote server' + '\r\n' + \
                  '13. `SYST` - Get server system information' + '\r\n' + \
                  '14. `FEAT` - Get the feature list implemented by the server' + '\r\n' + \
                  '15. `MDTM <file_name>` - Return the last-modified time of a specified file' + '\r\n' + \
                  '16. `QUIT` - quit connection' + '\r\n'
        massage = encode(self.encryption, massage, self.step)
        self.client.send(massage)

    def CWD(self, cmd):

        dest = os.path.join(self.cwd, cmd[4:].strip())
        if (os.path.isdir(dest)):
            self.cwd = dest
            massage = 'OK \"%s\".\r\n' % self.cwd
            massage = encode(self.encryption, massage, self.step)
            self.client.send(massage)
        else:
            print('ERROR: ' + str(self.client_address) + ': No such file or directory.')
            massage = '\"' + dest + '\": No such file or directory.\r\n'
            massage = encode(self.encryption, massage, self.step)
            self.client.send(massage)

    def AVBL(self, cmd):

        total, used, free = shutil.disk_usage("/")
        massage = 'Total: %d GiB' % (total // (2 ** 30)) + '\r\n' + \
                  'Used: %d GiB' % (used // (2 ** 30)) + '\r\n' + \
                  'Free: %d GiB' % (free // (2 ** 30)) + '\r\n'

        massage = encode(self.encryption, massage, self.step)
        self.client.send(massage)

    def CDUP(self, cmd):

        dest = os.path.abspath(os.path.join(self.cwd, '..'))
        if (os.path.isdir(dest)):
            self.cwd = dest
            massage = 'OK \"%s\".\r\n' % self.cwd
            massage = encode(self.encryption, massage, self.step)
            self.client.send(massage)
        else:
            print('ERROR: ' + str(self.client_address) + ': No such file or directory.')
            massage = '\"' + dest + '\": No such file or directory.\r\n'
            massage = encode(self.encryption, massage, self.step)
            self.client.send(massage)

    def MKD(self, cmd):

        path = cmd[4:].strip()
        dirname = os.path.join(self.cwd, path)
        try:
            if not path:
                massage = 'Missing arguments <dirname>.\r\n'
                massage = encode(self.encryption, massage, self.step)
                self.client.send(massage)
            else:
                os.mkdir(dirname)
                massage = 'Directory created: ' + dirname + '.\r\n'
                massage = encode(self.encryption, massage, self.step)
                self.client.send(massage)
        except Exception as e:
            print('ERROR: ' + str(self.client_address) + ': ' + str(e))
            massage = 'Failed to create directory ' + dirname + '.'
            massage = encode(self.encryption, massage, self.step)
            self.client.send('Failed to create directory ' + dirname + '.')

    def RMD(self, cmd):

        path = cmd[4:].strip()
        dirname = os.path.join(self.cwd, path)
        try:
            if not path:
                massage = 'Missing arguments <dirname>.\r\n'
                massage = encode(self.encryption, massage, self.step)
                self.client.send(massage)
            else:
                os.rmdir(dirname)
                massage = 'Directory deleted: ' + dirname + '.\r\n'
                massage = encode(self.encryption, massage, self.step)
                self.client.send(massage)
        except Exception as e:
            print('ERROR: ' + str(self.client_address) + ': ' + str(e))
            massage = 'Failed to delete directory ' + dirname + '.'
            massage = encode(self.encryption, massage, self.step)
            self.client.send(massage)

    def DELE(self, cmd):

        path = cmd[4:].strip()
        filename = os.path.join(self.cwd, path)
        try:
            if not path:
                massage = 'Missing arguments <filename>.\r\n'
                massage = encode(self.encryption, massage, self.step)
                self.client.send(massage)
            else:
                os.remove(filename)
                massage = 'File deleted: ' + filename + '.\r\n'
                massage = encode(self.encryption, massage, self.step)
                self.client.send(massage)
        except Exception as e:
            print('ERROR: ' + str(self.client_address) + ': ' + str(e))
            massage = 'Failed to delete file ' + filename + '.'
            massage = encode(self.encryption, massage, self.step)
            self.client.send(massage)

    def STOR(self, cmd):

        path = cmd[4:].strip()
        if not path:
            massage = 'Missing arguments <filename>.\r\n'
            massage = encode(self.encryption, massage, self.step)
            self.client.send(massage)
            return

        fname = os.path.join(self.cwd, path)
        (client_data, client_address) = self.start_datasock()

        try:
            file_write = open(fname, 'w')
            while True:
                data = client_data.recv(1024)
                data = decode(self.encryption, data, self.step)
                if not data:
                    break
                file_write.write(data)

            massage = 'Transfer complete.\r\n'
            massage = encode(self.encryption, massage, self.step)
            self.client.send(massage)
        except Exception as e:
            print('ERROR: ' + str(self.client_address) + ': ' + str(e))
            massage = 'Error writing file.\r\n'
            massage = encode(self.encryption, massage, self.step)
            self.client.send(massage)
        finally:
            client_data.close()
            self.close_datasock()
            file_write.close()

    def RETR(self, cmd):

        path = cmd[4:].strip()
        if not path:
            massage = 'Missing arguments <filename>.\r\n'
            massage = encode(self.encryption, massage, self.step)
            self.client.send(massage)
            return

        fname = os.path.join(self.cwd, path)
        (client_data, client_address) = self.start_datasock()
        if not os.path.isfile(fname):
            massage = 'File not found.\r\n'
            massage = encode(self.encryption, massage, self.step)
            self.client.send(massage)
        else:
            try:
                file_read = open(fname, "r")
                data = file_read.read(1024)

                while data:
                    data = encode(self.encryption, data, self.step)
                    client_data.send(data)
                    data = file_read.read(1024)

                massage = 'Transfer complete.\r\n'
                massage = encode(self.encryption, massage, self.step)
                self.client.send(massage)
            except Exception as e:
                print('ERROR: ' + str(self.client_address) + ': ' + str(e))
                massage = 'Connection closed; transfer aborted.\r\n'
                massage = encode(self.encryption, massage, self.step)
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

        massage = encode(self.encryption, massage, self.step)
        self.client.send(massage)

    def DSIZ(self, cmd):

        root_directory = Path('.')
        massage = 'Directory Size: ' + '\r\n' + \
                  str(sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file())) + ' (bytes)' + '\r\n' \
                  + str(
            sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file()) * 0.001) + ' KB' + '\r\n'

        massage = encode(self.encryption, massage, self.step)
        self.client.send(massage)

    def MDTM(self, cmd):

        path = cmd[4:].strip()
        if not path:
            massage = 'Missing arguments <filename>.\r\n'
            massage = encode(self.encryption, massage, self.step)
            self.client.send(massage)
            return

        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(path)
        massage = "last modified: %s" % time.ctime(mtime)

        massage = encode(self.encryption, massage, self.step)
        self.client.send(massage)

    def QUIT(self, cmd):

        try:
            massage = 'Quit - client logout\r\n'
            massage = encode(self.encryption, massage, self.step)
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

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = (self.address, self.port)

        try:
            print('Creating data socket on', self.address, ':', self.port, '...')
            self.sock.bind(server_address)
            self.sock.listen(5)
            print('Server is up. Listening to', self.address, ':', self.port)
        except Exception as e:
            print('Failed to create server on', self.address, ':', self.port, 'because', str(e.strerror))
            quit()

    def start(self):

        self.start_sock()

        try:
            while True:
                print('Waiting for a connection...')
                thread = FTPThreadServer(self.sock.accept(), self.address, self.data_port)
                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            print('Closing socket connection')
            self.sock.close()
            quit()

def users():
    key = 18
    users = pd.read_excel('clients.xlsx', index=False)
    while True:
        print('Current usernames and passwords are:\n')
        print(users)
        user = raw_input('Please enter a username\n')
        user = caesar_encode(user, key, mode = 1)
        passw = raw_input('Please enter a password\n')
        passw = caesar_encode(passw, key, mode = 1)
        print('Added successfully!')
        users.loc[len(users)] = {'username': user, 'password': passw}
        mor = raw_input('To add another user press [1] otherwise enter\n')
        if mor != '1':
            break
    users.to_excel('clients.xlsx', index=False)



#main

print('Welcome to FTP Server\n')

add_user = raw_input("Click [1] to add a new user to the system (If you leave empty, nothing will happen)\n")
if add_user == '1':
    users()

port = raw_input("Enter port: (if you left empty, default port is 10000)\n")
if not port:
    port = 10000

data_port = raw_input("Enter data port: (if you left empty, default port is 10001)\n")
if not data_port:
    data_port = 10001

server = FTPserver(port, data_port)
server.start()

