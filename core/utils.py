from io import BytesIO
from Crypto.Hash import MD5
from zipfile import ZipFile

def get_MD5(file: BytesIO):
    """
    Creates a MD5 hash of a file
    """
    chunk_size = 8192

    h = MD5.new()

    while True:
        chunk = file.read(chunk_size)
        if len(chunk):
            h.update(chunk)
        else:
            break

    return h.hexdigest()


def extract_zip(file, dir):
    """
    Extract zip file to `core/plugin/hash`
    """
    with ZipFile(file, 'r') as zipObj:
        zipObj.extractall(dir)