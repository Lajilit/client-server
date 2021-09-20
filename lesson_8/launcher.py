import subprocess

PROCESS = []

PROCESS.append(subprocess.Popen(
    'python server.py',
    creationflags=subprocess.CREATE_NEW_CONSOLE))
PROCESS.append(subprocess.Popen(
    'python client.py -n Kate',
    creationflags=subprocess.CREATE_NEW_CONSOLE))
PROCESS.append(subprocess.Popen(
    'python client.py -n John',
    creationflags=subprocess.CREATE_NEW_CONSOLE))
