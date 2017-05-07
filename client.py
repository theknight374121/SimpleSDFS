#!/usr/bin/env python
############################################################################
#
# Name: client.py
# Desc: Initial CLient for SDFS. 
# Author: Amey Patil
#
############################################################################

import socket, ssl
import sys
import getpass

def printListandChoice():
	'''
	Input: None
	Return: Choice (Integer)
	Desc: Prints the Menu for Clients and asks them to choose one options, then return the choose one
	'''
	while True:
		print "1-Create File"
		print "2-Read File"
		print "3-Write File"
		print "4-SetPermission"
		print "5-Delegate Permission"
		print "6-Logout"
		choice=int(raw_input("Enter your Choice:"))
		if choice < 7 and choice > 0:
			return choice
		else:
			print "Choice should be withn 1-6! Try Again!"
			continue

def handleMenu(ssl_conn):
	while True:
		choice=printListandChoice()
		if choice == 1:
			ssl_conn.send("1")
			handleCreateFile(ssl_conn)
		elif choice == 2:
			ssl_conn.send("2")
			handleReadFile(ssl_conn)
		elif choice == 3:
			ssl_conn.send("3")
			handleWriteFile(ssl_conn)
		elif choice == 4:
			ssl_conn.send("4")
			handleSetPermission(ssl_conn)
		elif choice == 5:
			ssl_conn.send("5")
			handleDelegatePermission(ssl_conn)
		elif choice ==6:
			ssl_conn.send("6")
			break
	return 

def handleCreateFile(ssl_conn):
	filename = raw_input("Enter filename:")
	
	#Send server filename
	sendPayload(ssl_conn, filename)

	#Receive server respsonse
	response=int(ssl_conn.recv(1))

	if response==1:
		print "Done creating File!"
	else:
		print "Error while creating File"
	return

def handleReadFile(ssl_conn):
	#Ask user filename
	filename = raw_input("Enter the filename:")
	#Check if this user has access to write to this file
	if hasFileAccess(ssl_conn, filename):
		#Receive the data
		data=receivePayload(ssl_conn)
		#Print the response
		print data
	else:
		print "No Access to read the file!"
	return
	
def handleWriteFile(ssl_conn):
	#Ask user filename
	filename = raw_input("Enter the filename:")
	#Check if this user has access to write to this file
	if hasFileAccess(ssl_conn, filename):
		#Ask for data
		data=raw_input("Enter data:")
		#Send the data
		sendPayload(ssl_conn, data)
		#Get the response
		response = int(ssl_conn.recv(1))
		if response == 1:
			print "Successfully added data"
		else:
			print "Error in adding data"
	else:
		print "No Access to write to this file!"
	return

def handleSetPermission(ssl_conn):
	#Ask filename you want to set permission for
	filename=raw_input("Enter filename:")

	#Check if this user has access to modify permissions of this file
	if hasFileAccess(ssl_conn, filename):
		#IF yes, ask the username and the permissions
		user=raw_input("Enter the user's name you want to give access:")
		permission=raw_input("Permission(R/W/RW):")

		#Creating the payload
		payload=list()
		payload.append(user)
		payload.append(permission)
		payload_str="|".join(payload)

		#Send payload
		sendPayload(ssl_conn, payload_str)

		#Receive server response
		response=int(ssl_conn.recv(1))
		if response==1:
			print "Successfully added permissions!!"
			return
		else:
			print "Error in adding permissions"
			return
	else:
		print "Access Denied! Only owner of the file can add permissions"
		return

def hasFileAccess(ssl_conn, filename):
	#Send server file name to check if user has access
	sendPayload(ssl_conn,filename)

	#Check server response
	response=int(ssl_conn.recv(1))
	
	if response == 1:
		return True
	else:
		return False

def handleDelegatePermission(ssl_conn):
	#Ask filename you want to delegate permission for
	filename=raw_input("Enter filename:")

	#Check if user is owner to delegate permsisions
	if hasFileAccess(ssl_conn, filename):
		user = raw_input("ENter the user's name:")

		#Send Payload
		sendPayload(ssl_conn, user)

		#Receive response
		response = int(ssl_conn.recv(1))
		if response==1:
			print "Successfully added permissions!!"
			return
		else:
			print "Error in adding permissions"
			return
	else:
		print "Access Denied! Only owner of the file can add permissions"
		return

	

def sendPayload(ssl_conn, data):
	len_str = str(len(data))
	pad = '0'*(5-len(len_str))
	return ssl_conn.send(pad+len_str+data)

def receivePayload(ssl_conn):
	length=int(ssl_conn.recv(5))
	payload = ssl_conn.recv(length)
	return payload

def setupConn(hostname):
	#Initialize context
	ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
	ctx.load_verify_locations('./demoCA/cacert.pem')
		
	#Setup Client socket
	ssl_conn = ctx.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM),server_hostname=hostname)
	
	#Connect to Server
	ssl_conn.connect((hostname, 33333))

	return ssl_conn

def handleLogin(ssl_conn):
	#Perform Login or Account Creation
	login_failed = True
	payload=list()
	while login_failed:
		choice = int(raw_input("1-Login\n2-Create Account\nEnter Choice: "))
		if choice == 1:
			#Let Server know that login is attempted
			ssl_conn.send("1")

		 	#User input for login 
			payload.append(raw_input("Username: "))
			payload.append(getpass.getpass())
			payload_str="|".join(payload)
			
			#Send login payload
			sendPayload(ssl_conn, payload_str)

			#Receive result
			result=int(ssl_conn.recv(1))
			if result == 0:
				#Login failed
				continue
			else:
				#Login succeeded
				return True

		elif choice == 2:
			#Let server know that account creation is attempted
			ssl_conn.send("2")
			#Create an account
		else:
			print "Invalid Option! Try Again \n"
	
	
def initiateConn():
    cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cli_socket.connect(('localhost', 33333))
    cli_socket.send('Hello')
    cli_socket.close()

def main():
	if len(sys.argv) < 2:
		print "You need to provide hostname of server. Needed for Server Cert Verification"
		return -1
	else:
		hostname = sys.argv[1]
		#Setup SSL
		ssl_conn=setupConn(hostname)
		#Handle Login
		if handleLogin(ssl_conn):
			#Run Menu Program
			handleMenu(ssl_conn)

if __name__ == '__main__':
    main()

