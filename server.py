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

class HandleClients(Thread):
	'''
	Thread Class to Handle Client Connections
	'''
	def __init__(self, sock, cli_details):
		Thread.__init__(self)
		self.sock = sock
		self.cli_addr = cli_details[0]
		self.cli_port = cli_details[1]
		print "Started a Thread for Client with addr={} and port={}".format(self.cli_addr, self.cli_port)

	def run(self):
		#Check what is being attempted
		choice=int(self.sock.recv(1))
		if choice == 1:
			#Handle login
			print "Reached Login"
		elif choice == 2:
			#Handle account creation
			print "TP"
		else:
			#Should never reach here. Redundant.
			print "Something wrong happened inside Login handling of thread that was handling Client with addr:{} and port:{}".format(self.cli_addr, self.cli_port)

		self.sock.close()

def setupSSL():
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
			newthread= HandleClients(ssl_sock, addr)
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
	
def main():
    setupSSL()

if __name__ == '__main__':
    main()
