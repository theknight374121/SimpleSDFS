#!/usr/bin/env python
############################################################################
#
# Name: server.py
# Desc: Main server program for SDFS. Handles all the connections 
# Author: Amey Patil
#
############################################################################

import ssl, socket
from threading import Thread
import MySQLdb
import getpass
import hashlib

class HandleClients(Thread):
	'''
	Thread Class to Handle Client Connections
	'''
	def __init__(self, sock, cli_details, dbconn):
		Thread.__init__(self)
		self.sock = sock
		self.cli_addr = cli_details[0]
		self.cli_port = cli_details[1]
		self.db = dbconn
		self.cli_username=""
		print "Started a Thread for Client with addr={} and port={}".format(self.cli_addr, self.cli_port)

	def run(self):
		#Handle initial login
		while True:
			#Check what is being attempted
			choice=int(self.sock.recv(1))
			if choice == 1:
				#Handle login
				if self.login():
					print "Login Successful!"
					# 1 to indicate success
					self.sock.send("1")
					break
				else:
					# 0  to indicate failure
					self.sock.send("0")
					continue
			elif choice == 2:
				#Handle account creation
				print "TP"
			else:
				#Should never reach here. Redundant.
				print "Something wrong happened inside Login handling of thread that was handling Client with addr:{} and port:{}".format(self.cli_addr, self.cli_port)

		#Listen for other instructions now
		while True:
			#Check what is being attempted:
			choice=int(self.sock.recv(1))
			if choice == 1:
				self.handleCreateFile()
			elif choice == 2:
				self.handleReadFile()
			elif choice == 3:
				self.handleWriteFile()
			elif choice == 4:
				self.handleSetPermission()
			elif choice == 5:
				self.handleDelegatePermission()
			elif choice == 6:
				self.logout()
				break
		#Exit thread			
		return

	def handleCreateFile(self):
		#Receive File name to create
		filename = self.receivePayload()

		#Create the file and add entry of it to the database
		with open(filename, "w") as file_obj:
			file_obj.close()

		#Add this filename to database
		query = ''' INSERT INTO files (filename, RDONLY, WRONLY, owner)  values (%s, %s, %s, %s)'''
		r_perm = self.cli_username
		w_perm = self.cli_username
		owner = self.cli_username
		values = (filename, r_perm, w_perm, owner)
		cursor = self.db.cursor()
		
		try:
			result=cursor.execute(query, values)
			self.db.commit()
		except MySQLdb.Error, e:
			print "Query error {}".format(str(e))

		#Add code to check if the query did successfully execute
		print result

		#Return success message
		self.sock.send("1")

		return

	def handleReadFile(self):
		#Receive Filename
		filename = self.receivePayload()
		#Check if has access
		if self.hasFileAccess(filename, 'R'):
			#IF yes pull data
			with open(filename, "r") as file_obj:
				data_list=file_obj.readlines()
				data_str="".join(data_list)
				self.sendPayload(data_str)
				file_obj.close()
		return

	def handleWriteFile(self):
		#Receive Filename
		filename = self.receivePayload()
		#Check if has access
		if self.hasFileAccess(filename, 'W'):
			#IF yes , receive data and add it to the file
			data = self.receivePayload()
			with open(filename, "w") as file_obj:
				file_obj.write(data)
				file_obj.close()
			#Return success message
			self.sock.send("1")

			return
		
	def hasFileAccess(self, filename, perm):
		#Check if the client is owner of the file
		query=''' SELECT RDONLY,WRONLY FROM files WHERE filename = %s'''
		values = (filename,)
		cursor = self.db.cursor()

		cursor.execute(query, values)
		r_perm, w_perm = cursor.fetchone()
		
		if perm == 'R':
			#Check if user has read access
			if self.cli_username in r_perm:
				self.sock.send("1")
				return True
			else:
				self.sock.send("0")
				return False
		elif perm == 'W':
			#Check if user has write access
			if self.cli_username in w_perm:
				self.sock.send("1")
				return True
			else:
				self.sock.send("0")
				return False

			
	def isOwner(self, filename):
		#Check if the client is owner of the file
		query=''' SELECT owner FROM files WHERE filename = %s'''
		values = (filename,)
		cursor = self.db.cursor()

		cursor.execute(query, values)
		owner = cursor.fetchone()
		
		if owner[0] == self.cli_username:
			#Send the Client that he has access
			self.sock.send("1")
			return True
		else:
			#Send Client that access denied
			self.sock.send("0")
			return False		
	
	def handleSetPermission(self):
		#Receive Filename from user
		filename=self.receivePayload()

		if self.isOwner(filename):
			#Fetch current permissions
			query = '''SELECT RDONLY, WRONLY FROM files WHERE filename = %s'''
			values = (filename,)
			cursor.execute(query, values)
			r_perm_e, w_perm_e = cursor.fetchone()

			print r_perm_e
			#if the owner is the user then set permissions
			data=self.receivePayload()
			data_list=data.split("|")
			#Set user
			user=data_list[0]
			#Set permission
			if data_list[1] == "R":
				r_perm = r_perm_e+":"+user
				values = (r_perm,filename)
			elif data_list[1] == "W":
				w_perm = w_perm_e+":"+user
				values = (w_perm,filename)
			elif data_list[1] == "RW":
				r_perm = r_perm_e+":"+user
				w_perm = w_perm_e+":"+user
				values = (r_perm, w_perm, filename)

			#Only supports read write
			query = ''' UPDATE files SET RDONLY=%s, WRONLY=%s WHERE filename=%s '''
			cursor.execute(query, values)
			self.db.commit()
			
			#Send success message
			self.sock.send("1")

		return

	def handleDelegatePermission(self):
		pass

	def logout(self):
		#Cleanua
		self.sock.close()
		self.db.close()

		#Logout message
		print "Logging Out!"
		return 
	
	def sendPayload(self, data):
		len_str = str(len(data))
		pad = '0'*(5-len(len_str))
		return self.sock.send(pad+len_str+data)


	def receivePayload(self):
		length=int(self.sock.recv(5))
		payload = self.sock.recv(length)
		return payload

	def login(self):
		#Receive Data
		payload=self.receivePayload()
		
		#Format the data
		payload_list = payload.split('|')
		username=payload_list[0]
		print "Username is {}".format(username)
		passwd = payload_list[1]
		
		#Prepare DB objects
		cursor = self.db.cursor()
		
		#Fetch Salt
		query = ''' select salt, password from users where name=%s '''
		values = (username,)
		cursor.execute(query, values)
		dbsalt, dbpwd = cursor.fetchone()
		#print "SAlt: {} and pwd:{}".format(dbsalt, dbpwd)
		hashpwd = hashlib.sha256(dbsalt+passwd).hexdigest()
		
		if hashpwd == dbpwd:
			self.cli_username=username
			return True
		else:
			return False

	def accountCreation(self):
		pass		

def setupDBConn():
	'''
	Set up connection to the Database
	'''
	#Fetch user password
	password=getpass.getpass("Enter Database Password:")

	#Initialize DB Connection
	try:
		db=MySQLdb.connect(host="127.0.0.1",user="CIS600",passwd=password,db="SimpleSDFS")
	except MySQLdb.Error, e:
		print "Could not connect to Database. Error message: %s".format(str(e))

	print "Successfully Connected to Database!!"
	return db

def setupSSL(dbconn):
	#Variables
	threads = list()

	#Initialize context
	ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
	ctx.load_cert_chain(certfile="server_signed_cert.pem", keyfile="./key/server_priv.pem")

	#Setup SSL Server Socket
	server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_sock.bind(('',33333))

	#Queue up max of 2 connections
	server_sock.listen(2)

	#This loop will never end hence add try catch
	try:
		#Handle those connections using a custom thread class
		while True:
			cli_sock, addr = server_sock.accept()
			ssl_sock = ctx.wrap_socket(cli_sock, server_side=True)
	
			#Create a thread to handle this connection
			newthread= HandleClients(ssl_sock, addr, dbconn)
			newthread.start()
	
			#Append this thread in a list to keep track
			threads.append(newthread)
	finally:
		#Close all sockets
		ssl_sock.close()
		server_sock.close()

		#Call for join on all threads before exiting
		for t in threads:
			t.join()
	
def cleanup():
	pass

def main():
	#Connect to DB
	dbconn=setupDBConn()
	setupSSL(dbconn)

if __name__ == '__main__':
    main()
