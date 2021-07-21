import time
import importlib
from action_provider import ActionProvider

def load_modules():
    """
    Dynamically load new modules in the plugins directory.
    The module has to be loaded as a separate directory and have a __init__.py file.
    """
    res = {}
    import os

    lst = os.listdir('./core/plugins')
    dir = []
    for d in lst:
        s = os.path.abspath('./core/plugins') + os.sep + d
        if os.path.isdir(s) and os.path.exists(s + os.sep + '__init__.py'):
            dir.append(d)
        
    for d in dir:
        res[d] = importlib.import_module('plugins.' + d + '.' + d)

    return res

if __name__ == '__main__':

    while True:
        load_modules() # Load possible new modules

        for action in ActionProvider.plugins:
            action().perform()
    
        time.sleep(10)
