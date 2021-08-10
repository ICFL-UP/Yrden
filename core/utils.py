import hashlib
import zipfile
from pathlib import Path


def md5_update_from_file(filename, hash):
    assert Path(filename).is_file()
    with open(str(filename), "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash


def md5_file(filename):
    return md5_update_from_file(filename, hashlib.md5()).hexdigest()


def md5_update_from_dir(directory, hash):
    assert Path(directory).is_dir()
    for path in sorted(Path(directory).iterdir()):
        hash.update(path.name.encode())
        if path.is_file():
            hash = md5_update_from_file(path, hash)
        elif path.is_dir():
            hash = md5_update_from_dir(path, hash)
    return hash


def md5_dir(directory):
    """
    Gets the hash of the contents of the specified directory.
    Sorts the contents to ensure the hash is the same everytime
    and any changes to any files will result in a different hash.
    """
    return md5_update_from_dir(directory, hashlib.md5()).hexdigest()


def extract_zip(file, directory):
    """
    Extract zip file to specified directory
    """
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(directory)