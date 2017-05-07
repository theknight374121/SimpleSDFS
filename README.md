This is a simple implementation of a Secure Distributed File System

Preparations:
1 - Make sure you have MySQL Server installed and running.
2 - Need to create a user called 'CIS600' and DBName as 'SimpleSDFS'
3 - The database should contain two tables - users, files.
4 - As of yet, the code doesn't support dymanic addition of such tables.
5 - Screenshots of such tables and their structure is given in the report.
6 - Once tables are ready. Users table need to be populated manually. It should contain atleast two users.

Run Instructions:
Terminal 1: $ python server.py
Terminal 2: $ python client.py www.simplesdfs.com
Terminal 3: $ python client.py www.simplesdfs.com

