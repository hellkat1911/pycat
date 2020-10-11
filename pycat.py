import sys
import socket
import getopt
import threading
import subprocess

# global definitions
listen = False
command = False
upload = False
execute = ""
target = ""
upload_dest = ""
port = 0

def usage():
    print("""        PyCat v1.0.0
        
        Usage: pycat.py -t target_host -p port
        -l --listen                 - listen on [host]:[port] for
                                      incoming connections
        -e -- execute=file_to_run   - execute the given file upon
                                      receiving a connection
        -c --commandshell           - initialize a command shell
        -u --upload=destination     - upon receiving connection upload
                                      a file and write to [destination]
                                         
        Examples:
        pycat.py -t 192.168.0.1 -p 5555 -l -c
        pycat.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe
        pycat.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"
        echo 'ABCDEFGHI' | ./pycat.py -t 192.168.0.1 -p 135
        
        written by: he77kat_
        inspired by: black hat python by justin seitz
    """)
    sys.exit(0)
    
def main():
    global listen
    global port
    global execute
    global command
    global upload_dest
    global target
    
    if not len(sys.argv[1:]):
        usage()
        
    # get command line flags
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu", ["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_dest = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"
            
    # listen or send data from stdin?
    if not listen and len(target) and port > 0:
    
        # read in buffer from the command line -
        # this will block, so use CTRL-D if not sending input to stdin
        
        buffer = sys.stdin.read()
        
        # send data
        client_sender(buffer)
        
    if listen:
        server_loop()
        
def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((target, port))
        
        if len(buffer):
            client.send(buffer)
            
            while True:
                # wait for response data
                recv_len = 1
                res = ""
                
                while recv_len:
                    data = client.recv(4096)
                    recv_len = len(data)
                    res += data
                    
                    if recv_len < 4096:
                        break
                        
                print(res)
                
                # wait for more input
                buffer = input("")
                buffer += "\n"
                
                client.send(buffer)
        
    except:
        print("[*] Exception! Exiting...")
        # clean up the connection
        client.close()
        
def server_loop():
    global target
    
    # if no target, listen on all interfaces
    if not len(target):
        target = "0.0.0.0"
        
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)
    
    while True:
        print("Listening on %s:%s..." % (target, port))
        client_socket, addr = server.accept()
        
        # spin up a thread to handle new client
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()
        
def run_command(command):
    # trim the newline
    command = command.rstrip()
    
    # run command and get the output
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"
    # send output to client
    return output
    
def client_handler(client_socket):
    global upload
    global execute
    global command
    
    # check for upload
    if len(upload_dest):
        file_buffer = ""
        # keep reading data until none is available
        while True:
            data = client_socket.recv(1024)
            
            if not data:
                break
            else:
                file_buffer += data
                
        # attempt to write out bytes
        try:
            fd = open(upload_dest, "wb")
            fd.write(file_buffer)
            fd.close()
            
            # ack that write was successful
            client_socket.send("Successfully saved file to %s\r\n" % upload_dest)
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_dest)
    
    # check for command execution
    if len(execute):
        output = run_command(execute)
        client_socket.send(output)
        
    # check if command shell was requested
    if command:
        while True:
            # simple prompt
            client_socket.send("<PyCat:#> ")
            
            # keep receiving until linefeed (ENTER key)
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
                
            # get command output
            res = run_command(cmd_buffer)
            client_socket.send(res)

if __name__ == "__main__":
    main()
        
        
        
        
        
        
        
        
        
        
        
        