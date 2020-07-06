# **File Transfer Protocol - Includes Encryption layer**


### **SCE 2020 - Data security project**


## **How to run**

- clone this project
- make sure you have python 3 installed, and Libraries: `socket`, `pandas`, `DES`, `xlsxwriter`.
- open terminal session and run the server by typing `python ftpserver.py` (by default server will use localhost, port 10000 for transfer &amp; 10001 for data transfer)

	Click [1] to add a new user to the system. (The usernames will be encrypted in the `clients.xlsx` file)
	
- In a different terminal session, run the client by typing `python ftpclient.py` (by default it will connect to localhost port 10000 &amp; 1000;) 
- Enter username and password to login:
- Select the required encryption [1] Caesar [2] DES

Caesar : https://en.wikipedia.org/wiki/Caesar_cipher
DES : https://en.wikipedia.org/wiki/Data_Encryption_Standard


- The server will provide a unique key to each client according to the code chosen by the client, and now all communications will be encrypted using that key.
	
	
- start to give command to the server (see some **commands** below)


## Supported commands

`ACCT` - Account information

`LIST` - information of a directory or file or information of current remote directory if not specified

`STOR <file_name>` - copy file to current remote directory 

`RETR <file_name>` - retrieve file from current remote directory

`AVBL` - Get the available space on server

`DSIZ` - Get the directory size

`PWD` - get current remote directory

`CDUP` - change to parent remote directory

`CWD <path>` - change current remote directory

`MKD <dir_name>` - make a directory in remote server

`RMD <dir_name>` - remove a directory in remote server

`DELE <file_name>` - delete a file in remote server 

`MDTM <file_name>` - Return the last-modified time of a specified file

`SYST` - Get server system information

`FEAT` - Get the feature list implemented by the server

`QUIT` - quit connection


Supported commands based on List of FTP commands in the link below:

https://en.wikipedia.org/wiki/List_of_FTP_commands


### **Milestones**

- Data security (Caesars Method, DES)
- Excel database management
- Socket
- Multiprocessing
- Read from arguments for server address &amp; ports


## Team:

roni goldsmid

yarden atias

moshiko bodaki


