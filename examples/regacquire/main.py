import os
import time
import shutil
import hashlib
import socket
import subprocess
import requests
import getpass
import datetime

from os.path import exists

URL='https://localhost:8000/pde/add/'
API_KEY='v1P6lqqT.a6Ew1Gjygq7GTemPxmL7LtuwPvEcAJnp'
API_SECRET='v1P6lqqT'
PLUGIN_USER='YRDEN_REGACQUIRE'

USER = getpass.getuser()
MACHINE = socket.gethostname()
IP = socket.gethostbyname(MACHINE)
NOW = datetime.datetime.now()
YEAR = '{:02d}'.format(NOW.year)
MONTH = '{:02d}'.format(NOW.month)
DAY = '{:02d}'.format(NOW.day)
YEAR_MONTH_DAY = '{}-{}-{}'.format(YEAR, MONTH, DAY)

SUCCESS = 0

def run():
    try:
        cwd = os.getcwd() + os.sep + 'core'
        if (exists('./dumps/'+USER+'_'+MACHINE+'_'+YEAR_MONTH_DAY)):
            subprocess.run(r'.\core\RegAcquire.exe', cwd=cwd, input=b'y\n')
        else:
            subprocess.run(r'.\core\RegAcquire.exe', cwd=cwd, input=b'\n')

    except subprocess.CalledProcessError as cpe:
        print(cpe.stdout.decode('utf-8'))
        print(cpe.stderr.decode('utf-8'))

def save_data():
    global SUCCESS

    name = get_data()

    hash_md5 = hashlib.md5()
   
    with open(name, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    data = {
        'ip': IP,
        'machine': MACHINE,
        'filename': 'Evi_' + str(name),
        'user': PLUGIN_USER,
        'rank': 0,
        'md5sum': hash_md5.hexdigest(),
        'token': API_KEY
    }
    file = open(name, 'rb')
    files = {'pde': file}
    headers = {
        'Api-Secret-Key': API_SECRET,
        'Api-Token': API_KEY,
        'X-Api-Key': API_KEY,
        'Authorization': 'Token ' + API_KEY,
        'Token': API_KEY,
    }

    r = requests.post(url=URL, data=data, headers=headers, files=files, verify=False)
    file.close()
    print(r.text)
    if "Success" in r.text:
        SUCCESS += 1

def delete_files():
    dumps = 'core' + os.sep + 'dumps'
    console_mode = 'core' + os.sep + 'ConsoleMode.txt'
    evidence_log = 'core' + os.sep + 'evidence.log'
    hash = 'core' + os.sep + 'hash.hash'
    evidence = 'evidence'
    remove_paths = [dumps, console_mode, evidence_log, hash, evidence]

    for path in remove_paths:
        if os.path.isdir(path):
            try:
                os.system('rmdir /S /Q "{}"'.format(path))
            except OSError as e:
                print(e)

        elif os.path.isfile(path):
            try:
                os.remove(path)
            except OSError as e:
                print(e)
        

def get_data():
    evidence_name = './evidence/' + time.strftime("%Y%m%d-%H%M%S")
    return shutil.make_archive(evidence_name, 'zip', root_dir=os.getcwd() + os.sep + 'core', base_dir='dumps' + os.sep + USER + '_' + MACHINE + '_' + YEAR_MONTH_DAY)

def stats():
    print("Success: ", SUCCESS)

if __name__ == "__main__":
    run()
    save_data()
    stats()
    delete_files()
