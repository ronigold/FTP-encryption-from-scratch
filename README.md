# SCE 2020 Data security project

## How to run

1. Open cmd Windows in server machine and enter to path `cd../FTP_encoded_from_scratch`
2. Open the server file for the server run `python ftpserver.py`
3. Open cmd Windows in Client machine and enter to path `cd../FTP_encoded_from_scratch`
4. Open the client file for the client run `python ftpclient.py`
5. You can add more clients as you want. The system supports multi-processors. Just repeat steps (3-4)

## Supported commands

`LIST <path>` - nformation of a directory or file or information of current remote directory if not specified

`STOR <file_name>` - copy file to current remote directory 

`RETR <file_name>` - retrieve file from current remote directory

`PWD` - get current remote directory

`CDUP` - change to parent remote directory

`CWD <path>` - change current remote directory

`MKD` - make a directory in remote server

`RMD <dir_name>` - remove a directory in remote server

`DELE <file_name>` - delete a file in remote server 

`QUIT` - quit connection


## Team:

roni goldsmid

yarden atias

moshiko bodaki


