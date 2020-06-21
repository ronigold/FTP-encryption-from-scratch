# **File Transfer Protocol - Caesars Method**


### **SCE 2020 - Data security project**


## **How to run**
- clone this project
- make sure you have python 3 installed, and Libraries: `socket`, `pandas`.
- open terminal session and run the server by typing `python ftpserver.py` (by default server will use localhost, port 10021 for transfer &amp; 10020 for data transfer)
- In a different terminal session, run the client by typing `python ftpclient.py` (by default it will connect to localhost port 10021 &amp; 10020) 
- Enter username and password to login:

	a. username: `<roni>`, password: `<abcdefg>` 
	
	a. username: `<sce>`, password: `<qwer>` 
	
	the username and password read from exel `clients` file. to add mor clients add rows in this file.
	
- start to give command to the server (see some **commands** below)


## Supported commands

`LIST` - nformation of a directory or file or information of current remote directory if not specified

`STOR <file_name>` - copy file to current remote directory 

`RETR <file_name>` - retrieve file from current remote directory

`PWD` - get current remote directory

`CDUP` - change to parent remote directory

`CWD <path>` - change current remote directory

`MKD <dir_name>` - make a directory in remote server

`RMD <dir_name>` - remove a directory in remote server

`DELE <file_name>` - delete a file in remote server 

`SYST` - Get server system information

`QUIT` - quit connection


### **Milestones**

- Data security (Caesars Method)
- Excel database management
- Socket
- Multiprocessing
- Read from arguments for server address &amp; ports


## Team:

roni goldsmid

yarden atias

moshiko bodaki


