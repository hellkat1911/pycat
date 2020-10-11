# PyCat

A netcat implementation written in Python.

Usage: pycat.py -t target_host -p port

-l --listen<br>
&nbsp;&nbsp;&nbsp;&nbsp;listen on [host]:[port] for incoming connections

-e -- execute=file_to_run<br>
&nbsp;&nbsp;&nbsp;&nbsp;execute the given file upon receiving a connection

-c --commandshell<br>
&nbsp;&nbsp;&nbsp;&nbsp;initialize a command shell

-u --upload=destination<br>
&nbsp;&nbsp;&nbsp;&nbsp;upon receiving connection upload a file and write to destination
                                  
**Examples:**

pycat.py -t 192.168.0.1 -p 5555 -l -c<br>
pycat.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe<br>
pycat.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"<br>
echo 'ABCDEFGHI' | ./pycat.py -t 192.168.0.1 -p 135<br>

<hr>

written by: he77kat_<br>
inspired by: black hat python by justin seitz