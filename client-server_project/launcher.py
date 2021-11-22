import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('count', type=int, help='Количество клиентских приложений')
args = parser.parse_args()
PROCESS = [subprocess.Popen(
    'python server.py',
    creationflags=subprocess.CREATE_NEW_CONSOLE)]

for i in range(args.count):
    PROCESS.append(subprocess.Popen(
        f'python client.py -n guest{i+1}',
        creationflags=subprocess.CREATE_NEW_CONSOLE))
