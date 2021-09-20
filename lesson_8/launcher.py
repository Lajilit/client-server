import subprocess


PROCESS = []

PROCESS.append(subprocess.Popen(
    'python server.py -a 127.0.0.1 -p 8080',
    creationflags=subprocess.CREATE_NEW_CONSOLE))
for i in range(2):
    PROCESS.append(subprocess.Popen(
        'python client.py -n Kate 127.0.0.1 8080',
        creationflags=subprocess.CREATE_NEW_CONSOLE))
for i in range(2):
    PROCESS.append(subprocess.Popen(
        'python client.py -n John 127.0.0.1 8080',
        creationflags=subprocess.CREATE_NEW_CONSOLE))
