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
	print "To be Continued"

def setupConn(hostname):
	#Initialize context
	ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
	ctx.load_verify_locations('./demoCA/cacert.pem')
		
	#Setup Client socket
	ssl_conn = ctx.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM),server_hostname=hostname)
	
	#Connect to Server
	ssl_conn.connect((hostname, 33333))
	
	#Perform Login or Account Creation
	login_failed = True
	while login_failed:
		choice = int(raw_input("1-Login\n2-Create Account\nEnter Choice: "))
		if choice == 1:
			#Let Server know that login is attempted
			ssl_conn.send("1")
			return 
		 	# TODO Convert this input to join 
			username = raw_input("Username:")
			password = getpass.getpass()
			payload=username+"|"+password
			ssl_conn.send(payload)
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
		setupConn(hostname)

if __name__ == '__main__':
    main()

