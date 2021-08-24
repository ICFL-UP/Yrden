import os
import json
import zipfile
import datetime
import subprocess
import logging

from io import BufferedReader
from typing import Union
from hashlib import md5

from core.models import Plugin
from core.exceptions import HashJSONFailedException

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-9s) %(message)s',)


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


# TODO: Need to raise warning if extra files not in JSON
def validate_dir(directory: str, relative_path: str, hash_dict: dict):
    """
    Recursive method to validate subdirectories
    """
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)

        if os.path.isfile(f):
            source_hash = hash_dict[relative_path + filename]
            plugin_hash = get_MD5(f)

            if source_hash != plugin_hash:
                raise HashJSONFailedException(
                    f'Hash for {relative_path + filename} [{source_hash}] does not match computed hash [{plugin_hash}]')

        elif os.path.isdir(f) and filename != '.venv':
            validate_dir(directory + os.sep + filename, relative_path +
                         filename + '/', hash_dict)


def validate_plugin_hash(plugin: Plugin) -> bool:
    """
    Validate the plugin source file hashes
    """
    validate_dir(plugin.plugin_dest, '', json.loads(
        plugin.plugin_source.source_file_hash))
