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

def setupConn():
	#Initialize context
	ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
	ctx.load_verify_locations('./demoCA/cacert.pem')
		
	#ssetup client
	#ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
	#context.verify_mode = ssl.CERT_REQUIRED
	#context.check_hostname = True
	#context.load_verify_locations("/etc/ssl/certs/ca-bundle.crt")
	ssl_conn = ctx.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM),server_hostname=sys.argv[1])
	ssl_conn.connect((sys.argv[1], 33333))
	ssl_conn.send('Hello')
	ssl_conn.close()
	
def initiateConn():
    cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cli_socket.connect(('localhost', 33333))
    cli_socket.send('Hello')
    cli_socket.close()

def main():
    setupConn()

if __name__ == '__main__':
    main()

