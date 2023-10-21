import sys

import socket

# Parse command-line arguments
server_host = sys.argv[1]
server_port = int(sys.argv[2])
message_filename = sys.argv[3]
signature_filename = sys.argv[4]

"""print(server_name, '\n')
print(server_port, '\n')
print(message_filename, '\n')
print(signature_filename, '\n')
"""
# Read messages from the message file

    
messages = []
with open(message_filename, 'r') as message_file:
    while True:
        line = message_file.readline()
        if not line:
            break
        linenum = int(line)
        msg = message_file.readline()
        #print(msg, "\n")
        byte_array = bytearray()
        modified_message = msg.replace('.', '\.').replace('\\', '\\')
        byte_array = modified_message.encode('ascii')
          
        """ for char in msg:
            if(char == '.'):
                byte_array.append(ord('\\'))
                byte_array.append(ord(char))
            elif char == "\\":
                byte_array.append(ord('\\'))
            else:
                byte_array.append(ord(char))
                """  
        #print(byte_array)     
        messages.append(byte_array)
#print(messages)
# Read signatures from the signature file
#print("DBG: NUmber of msgs= ", len(messages))
new_line = b'\n'
messages[len(messages)-1] += new_line
#print( "DBG: Last message: ", messages[len(messages)-1] )
signatures = []
with open(signature_filename, 'r') as signature_file:
    while True:
        line = signature_file.readline()
        line = line[:-1]
        if not line:
            break
        signatures.append(line)
#print("DBG:Length of sig: " , len(signatures[0]))            

# Open a TCP socket to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#client_socket.settimeout(1) # timeout value = 2s
client_socket.connect((server_host, server_port))
#print("DBG: Connected to server..........................\n")
# Send a "HELLO" message to the server
client_socket.sendall(b"HELLO\n")
response = client_socket.recv(1024).decode().strip()
print(response)
#response = response.strip()
if response != "260 OK":
    print("Error: Server did not respond with '260 OK'")
    client_socket.close()
    sys.exit(1)
      

# Initialize message counter
message_counter = 0

# Send messages to the server and verify signatures
for message in messages:
    
   # print("DBG: ",message, end ='\n')                 
    client_socket.sendall(b"DATA\n")
    client_socket.sendall(message)
    client_socket.sendall(b".\n")
    response = client_socket.recv(1024).decode().strip()
    print(response)
    if response != "270 SIG":
        print("Error: Expected '270 SIG' from the server")
        client_socket.close()
        sys.exit(1)

    server_signature = client_socket.recv(1024).decode().strip()# expcted length of each sig is 64
    print(server_signature)
    if server_signature == signatures[message_counter]:
        client_socket.sendall(b"PASS\n")
    else:
        client_socket.sendall(b"FAIL\n")

    response = client_socket.recv(1024).decode().strip()
    print(response)
    if response != "260 OK":
        print("Error: Server did not respond with '260 OK'")
        client_socket.close()
        sys.exit(1)

    message_counter += 1
#client_socket.sendall(b".")
# Send a "QUIT" message to the server
client_socket.sendall(b"QUIT\n")

# Close the TCP socket
client_socket.close()
         
     