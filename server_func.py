from encoded import *
import os
import shutil
from pathlib import Path
import time
import platform

def ACCT(self, cmd):
    massage = '------- Account information -------' + '\r\n' + \
              'You are login in as:  ' + self.username + '\r\n' + \
              'Your address is:  ' + str(self.client_address) + '\r\n'

    massage = caesar_encode(massage, self.step)
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
        massage = caesar_encode(table, self.step)
        client_data.send(massage)

        for i in listdir:
            path = os.path.join(self.cwd, i)
            stat = os.stat(path)
            data = '| %*s | %9s | %12s | %20s | %11s | %12s |\n' % (
            max_length, i, 'Directory' if os.path.isdir(path) else 'File', str(stat.st_size) + 'B',
            time.strftime('%b %d, %Y %H:%M', time.localtime(stat.st_mtime))
            , oct(stat.st_mode)[-4:], str(stat.st_uid) + '/' + str(stat.st_gid))
            massage = caesar_encode(data, self.step)
            client_data.send(massage)

        table = '%s\n' % ('-' * len(header))
        massage = caesar_encode(table, self.step)
        client_data.send(massage)

        massage = '\r\nDirectory send OK.\r\n'
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


def PWD(self, cmd):
    massage = '\"%s\".\r\n' % self.cwd
    massage = caesar_encode(massage, self.step)
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

    massage = caesar_encode(massage, self.step)
    self.client.send(massage)


def CWD(self, cmd):
    dest = os.path.join(self.cwd, cmd[4:].strip())
    if (os.path.isdir(dest)):
        self.cwd = dest
        massage = 'OK \"%s\".\r\n' % self.cwd
        massage = caesar_encode(massage, self.step)
        self.client.send(massage)
    else:
        print('ERROR: ' + str(self.client_address) + ': No such file or directory.')
        massage = '\"' + dest + '\": No such file or directory.\r\n'
        massage = caesar_encode(massage, self.step)
        self.client.send(massage)


def AVBL(self, cmd):
    total, used, free = shutil.disk_usage("/")
    massage = 'Total: %d GiB' % (total // (2 ** 30)) + '\r\n' + \
              'Used: %d GiB' % (used // (2 ** 30)) + '\r\n' + \
              'Free: %d GiB' % (free // (2 ** 30)) + '\r\n'

    massage = caesar_encode(massage, self.step)
    self.client.send(massage)


def CDUP(self, cmd):
    dest = os.path.abspath(os.path.join(self.cwd, '..'))
    if (os.path.isdir(dest)):
        self.cwd = dest
        massage = 'OK \"%s\".\r\n' % self.cwd
        massage = caesar_encode(massage, self.step)
        self.client.send(massage)
    else:
        print('ERROR: ' + str(self.client_address) + ': No such file or directory.')
        massage = '\"' + dest + '\": No such file or directory.\r\n'
        massage = caesar_encode(massage, self.step)
        self.client.send(massage)


def MKD(self, cmd):
    path = cmd[4:].strip()
    dirname = os.path.join(self.cwd, path)
    try:
        if not path:
            massage = 'Missing arguments <dirname>.\r\n'
            massage = caesar_encode(massage, self.step)
            self.client.send(massage)
        else:
            os.mkdir(dirname)
            massage = 'Directory created: ' + dirname + '.\r\n'
            massage = caesar_encode(massage, self.step)
            self.client.send(massage)
    except Exception as e:
        print('ERROR: ' + str(self.client_address) + ': ' + str(e))
        massage = 'Failed to create directory ' + dirname + '.'
        massage = caesar_encode(massage, self.step)
        self.client.send('Failed to create directory ' + dirname + '.')


def RMD(self, cmd):
    path = cmd[4:].strip()
    dirname = os.path.join(self.cwd, path)
    try:
        if not path:
            massage = 'Missing arguments <dirname>.\r\n'
            massage = caesar_encode(massage, self.step)
            self.client.send(massage)
        else:
            os.rmdir(dirname)
            massage = 'Directory deleted: ' + dirname + '.\r\n'
            massage = caesar_encode(massage, self.step)
            self.client.send(massage)
    except Exception as e:
        print('ERROR: ' + str(self.client_address) + ': ' + str(e))
        massage = 'Failed to delete directory ' + dirname + '.'
        massage = caesar_encode(massage, self.step)
        self.client.send(massage)


def DELE(self, cmd):
    path = cmd[4:].strip()
    filename = os.path.join(self.cwd, path)
    try:
        if not path:
            massage = 'Missing arguments <filename>.\r\n'
            massage = caesar_encode(massage, self.step)
            self.client.send(massage)
        else:
            os.remove(filename)
            massage = 'File deleted: ' + filename + '.\r\n'
            massage = caesar_encode(massage, self.step)
            self.client.send(massage)
    except Exception as e:
        print('ERROR: ' + str(self.client_address) + ': ' + str(e))
        massage = 'Failed to delete file ' + filename + '.'
        massage = caesar_encode(massage, self.step)
        self.client.send(massage)


def STOR(self, cmd):
    path = cmd[4:].strip()
    if not path:
        massage = 'Missing arguments <filename>.\r\n'
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

        massage = 'Transfer complete.\r\n'
        massage = caesar_encode(massage, self.step)
        self.client.send(massage)
    except Exception as e:
        print('ERROR: ' + str(self.client_address) + ': ' + str(e))
        massage = 'Error writing file.\r\n'
        massage = caesar_encode(massage, self.step)
        self.client.send(massage)
    finally:
        client_data.close()
        self.close_datasock()
        file_write.close()