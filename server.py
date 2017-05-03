#!/usr/bin/env python
############################################################################
#
# Name: server.py
# Desc: Main server program for SDFS. Handles all the connections 
# Author: Amey Patil
#
############################################################################

import ssl
import socket

def setupSSL():
	#Initialize context
	ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
	ctx.load_cert_chain(certfile="server_signed_cert.pem", keyfile="./key/server_priv.pem")
	
	#SetupServer
	server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_sock.bind(('',33333))
	server_sock.listen(1)
	newsock, addr = server_sock.accept()
	ssl_sock = ctx.wrap_socket(newsock, server_side=True)
	data=ssl_sock.recv(4096)
	print data
	ssl_sock.close()
	
def initiateServer():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 33333))
    server_socket.listen(1)
    (cli_socket, address) = server_socket.accept()
    print address
    rec_data=cli_socket.recv(4096)
    print rec_data
    server_socket.close()
    cli_socket.close()

def main():
    setupSSL()

if __name__ == '__main__':
    main()
