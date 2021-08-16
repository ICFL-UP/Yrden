import os
from io import BufferedReader
from typing import Union
from Crypto.Hash import MD5
import zipfile


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

    h = MD5.new()

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


def extract_zip(file, directory):
    """
    Extract zip file to specified directory
    """
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(directory)


def delete_dir(directory):
    """
    Removes the specified directory
    """
    os.rmdir(directory)