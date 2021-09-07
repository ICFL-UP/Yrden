import io
import os
import json
import zipfile
import subprocess
import logging

from io import BufferedReader
from typing import Union
from hashlib import md5
from django.utils import timezone
from datetime import datetime

from core.enums.log_type_enum import LogType
from core.exceptions import HashJSONFailedException
from core.enums.plugin_status import PluginStatus

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


def build_zip_json(zip_bytes: io.BytesIO, plugin_source) -> None:
    """
    Builds a JSON file of the zip contents hashing each file and storing the hash.
    {
        filename: hash,
        directory/filename: hash
    }
    """
    data = {}

    zip = zipfile.ZipFile(zip_bytes)
    for name in zip.namelist():
        if not name.endswith('/'):
            with zipfile.ZipFile.open(zip, name) as memberFile:
                data[name] = get_MD5(memberFile)

    plugin_source.source_file_hash = json.dumps(data)
    plugin_source.save()

    log_json: dict = {
        'log_datetime': datetime.timestamp(timezone.now()),
        'source_dest': plugin_source.source_dest,
        'source_hash': plugin_source.source_hash,
        'source_file_hash': json.loads(plugin_source.source_file_hash),
    }
    write_log(LogType.HASH_LIST, plugin_source, log_json)


def datetime_to_string(timezone: timezone) -> str:
    return datetime.strftime(timezone, "%m/%d/%Y, %H:%M:%S")


def write_log(log_type: LogType, plugin_source, log: dict) -> None:
    path = plugin_source.source_dest + os.sep + log_type.value + '_' + \
        str(datetime.timestamp(plugin_source.upload_time)) + '.json'

    with open(path, 'x') as file:
        file.write(json.dumps(log))


def run_subprocess(command: 'list[str]', timeout=None, shell=False) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, shell=shell)


def create_venv(plugin):
    """
    Create virtual env for the specified plugin
    """
    try:
        plugin.status = PluginStatus.VIRTUALENV
        plugin.save()

        venv_dest = plugin.plugin_dest + os.sep + '.venv'

        venv_command = [
            'python',
            '-m',
            'virtualenv',
            venv_dest,
            '-p',
            plugin.python_version
        ]
        venv_process: subprocess.CompletedProcess = run_subprocess(
            venv_command)

        plugin.status = PluginStatus.DEPENDECIES
        plugin.stdout = venv_process.stdout.decode('utf-8')
        plugin.stderr = venv_process.stderr.decode('utf-8')
        plugin.save()

        python = venv_dest + os.sep + 'bin' + os.sep + 'python'
        requirements = plugin.plugin_dest + os.sep + 'requirements.txt'

        deps_command = [
            python,
            '-m',
            'pip',
            'install',
            '-r',
            requirements
        ]
        deps_process: subprocess.CompletedProcess = run_subprocess(
            deps_command)

        plugin.status = PluginStatus.SUCCESS
        plugin.stdout = deps_process.stdout.decode('utf-8')
        plugin.stderr = deps_process.stderr.decode('utf-8')
        plugin.save()
    except subprocess.CalledProcessError as cpe:
        plugin.status = PluginStatus.Failed
        plugin.stdout = cpe.stdout.decode('utf-8')
        plugin.stderr = cpe.stderr.decode('utf-8')
        plugin.save()

    plugin.save()


# TODO: https://github.com/ICFL-UP/Yrden/issues/29
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


def validate_plugin_hash(plugin) -> bool:
    """
    Validate the plugin source file hashes
    """
    validate_dir(plugin.plugin_dest, '', json.loads(
        plugin.plugin_source.source_file_hash))


def get_python_choices() -> 'list[(int, str)]':
    cmd = 'find /bin/ -type f -executable -print -exec file {} \\; | grep python | grep -wE "ELF" | grep -o "\\/bin\\/.*:"'

    python_versions_cp = run_subprocess([cmd], shell=True)

    versions = python_versions_cp.stdout.decode('utf-8').split('\n')
    python_versions: list[str] = []
    for version in versions:
        if version.startswith('/bin/'):
            python_versions.append(version[:-1])

    python_choices = []
    for index, value in enumerate(python_versions):
        val = (index, value)
        python_choices.append(val)

    return python_choices
