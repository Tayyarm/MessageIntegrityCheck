import socket
import hashlib
import sys
import time 

server_host = "localhost"
def main():
    if len(sys.argv) != 3:
        print("Usage: python3 server.py <listen-port> <key-file>")
        return

    listen_port = int(sys.argv[1])
    key_file = sys.argv[2]

    # Read keys from the key-file
    keys = []
    with open(key_file, 'r') as key_file:
        while True:
            line = key_file.readline()
            line = line[:-1]
            if not line:
                break
            keys.append(line)
    #with open(key_file, 'r') as key_file:
     #   keys = [line.strip() for line in key_file]
  #  print("DBG: Len of key:" ,len(keys[0]))
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_host, listen_port))
    server_socket.listen(1)

    #print(f"Server listening on port {listen_port}")
    buffer = ""
    alive = False
    while True:
        if not alive:
           # print("DBG: Waiting for client connection---------------------\n")
            client_socket, client_addr = server_socket.accept()
           # print(f"DBG: Connection from {client_addr}")
            alive =True
        else: 
        # Read the first line from the client
            command = client_socket.recv(1).decode()
           # print("___________________________-")
            if not command:
                alive = False
                continue
           # print(f"received data:{command}")  
            if command != '\n':
                buffer+=command
                continue
            print(buffer)
            if buffer != "HELLO":
                print("Error: Unexpected command. Closing the connection.")
                client_socket.close()
                sys.exit(1)
            else:
                #print("sending 260 OK")
                client_socket.sendall(b"260 OK")
                break
    msg_counter = 0        
    buffer = ""
    PASS_FAIL_FLAG = False
    msg = False
    isEscape= False
    Actual_Message = ""
    while True:
        if not alive:
            client_socket, client_addr = server_socket.accept()
           # print(f"DBG: Connection from {client_addr}")
            alive =True
            buffer = ""
            PASS_FAIL_FLAG = False
            msg = False
            isEscape= False
        else: 
            data = client_socket.recv(1).decode()
            if not data:
               #print("DBG: NULL DATA RECIVED") 
               alive = False
               continue
           #data = chr(data[0])
            if data == '\\':
                if isEscape == True:
                    isEscape = False
                    buffer += data       
                else: 
                    isEscape=True
                continue
           # if data =='.' and not isEscape:
            #   break     
            if data != '\n':              
                buffer += data                    
                continue
            
            if data == '\n':
                print(buffer)
                if buffer == "DATA" and not msg: 
                    msg = True #indicator that next data value will be a message sent by client
                    buffer = "" 
                   # PASS_FAIL_FLAG = False
                    isEscape= False
                  # continue   
                elif buffer =="QUIT" and not msg:
                    server_socket.close()
                    sys.exit(0)
                elif PASS_FAIL_FLAG == True :
                   # print("DBG: PASS-FAIL_CODE_BLOCK")
                    if buffer == "PASS" or buffer == "FAIL":
                        PASS_FAIL_FLAG = False
                        #time.sleep(1)
                      #  print("Recieved:", buffer)
                        client_socket.sendall(b"260 OK")
                        buffer = ""
                        continue
                    else:
                      print(" Error Response from client")
                      sys.exit(1)
                elif buffer == ".":
                    client_socket.sendall(b"270 SIG")   
                    sha256_hash = hashlib.sha256()
                    Actual_Message = (Actual_Message+keys[msg_counter]).encode()
                    sha256_hash.update(Actual_Message)
                    #sha256_hash.update(keys[msg_counter].encode())
                    msg_counter +=1
                 #   response = hashlib.sha256(Actual_Message).hexdigest()
                    response = sha256_hash.hexdigest()
                    time.sleep(1)
                   # print("DBG: ", response.encode()) 
                    client_socket.sendall(response.encode())
                    PASS_FAIL_FLAG=True
                    msg = False
                    buffer =""
                    
                else: # we'll process msg over here
                    Actual_Message = buffer
                    buffer = ""
                    msg = False
                    #client_socket.sendall(b"270 SIG")   
                    #sha256_hash = hashlib.sha256()  
                    #sha256_hash.update(buffer.encode())
                    #sha256_hash.update(keys[msg_counter].encode()) 
                    #msg_counter +=1
                  #  response = sha256_hash.hexdigest()
                   # time.sleep(1)
                   # client_socket.sendall(d.encode()) 
                  #  print("DBG: ", response.encode()) 
                    #client_socket.sendall(response.encode())
                    #PASS_FAIL_FLAG=True
                    #buffer =""
                    #print(response)
                    #client_socket.sendall(b'response')
                #print("DBG: end of While loop----------------\n")
                
                
                
                                  
"""            
     if not command:
            break
           
        if command == "DATA":
            sha256_hash = hashlib.sha256()
            while True:
                line = client_socket.recv(1024).decode()
                if line == ".":
                    break
                line = line.encode().decode('unicode_escape')
                sha256_hash.update(line.encode())
            key = keys.pop(0) if keys else "default_key"
            sha256_hash.update(key.encode())
            response = f"270 SIG {sha256_hash.hexdigest()}\n"
            client_socket.send(response.encode())

            command = client_socket.recv(1024).decode()
            if command != "PASS" and command != "FAIL":
                print("Error: Unexpected command. Closing the connection.")
                client_socket.close()
                break

            response = "260 OK\n"
            client_socket.send(response.encode())
        elif command == "QUIT":
            client_socket.close()
            break
        else:
            print("Error: Invalid command. Closing the connection.")
            client_socket.close()
            break
"""
if __name__ == "__main__":
    main()