import os
import json
import zipfile
import datetime
import subprocess

from io import BufferedReader
from typing import Union
from hashlib import md5

from core.models import Plugin


def get_MD5(file: Union[BufferedReader, str]) -> str:
    """
    Creates a MD5 hash of a file
    """
    buffered_file: BufferedReader = None
    if isinstance(file, str):
        buffered_file = open(file, 'rb')
    else:
        buffered_file = file

    chunk_size = 8192

    h = md5()

    while True:
        chunk = buffered_file.read(chunk_size)
        if len(chunk):
            h.update(chunk)
        else:
            break

    return h.hexdigest()


def store_zip_file(file: BufferedReader, directory: str) -> None:
    """Stores the file in the given directory"""
    os.mkdir(directory)
    with open(directory + os.sep + file.name, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def extract_zip(file: BufferedReader, directory: str):
    """
    Extract zip file to specified directory
    """
    with zipfile.ZipFile(file, 'r') as zip:
        zip.extractall(directory)


def build_zip_json(zip: zipfile.ZipFile) -> str:
    """
    Builds a JSON file of the zip contents hashing each file and storing the hash.
    {
        filename: hash,
        directory/filename: hash
    }
    """
    data = {}

    for name in zip.namelist():
        if not name.endswith('/'):
            with zipfile.ZipFile.open(zip, name) as memberFile:
                data[name] = get_MD5(memberFile)

    return json.dumps(data)


def datetime_to_string(datetime: datetime.datetime) -> str:
    return datetime.strftime("%m/%d/%Y, %H:%M:%S")


# TODO: https://github.com/ICFL-UP/Yrden/issues/26
def create_venv(plugin: Plugin):
    """
    Create virtual env for the specified plugin
    """
    venv_dest = plugin.plugin_dest + os.sep + '.venv'
    subprocess.run(['python', '-m', 'virtualenv',
                    venv_dest, '-p', 'python'])

    python = venv_dest + os.sep + 'bin' + os.sep + 'python'
    requirements = plugin[0].plugin_dest + os.sep + 'requirements.txt'
    subprocess.run(
        [python, '-m', 'pip', 'install', '-r', requirements])
