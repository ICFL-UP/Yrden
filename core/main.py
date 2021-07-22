import importlib
import logging
import sys
from action_provider import ActionProvider

from threading import Timer, Lock
from time import sleep

logging.basicConfig(level=logging.WARN,
                    format='(%(threadName)-9s) %(message)s',)
logger = logging.getLogger('main')

"""
List of plugins
"""
plugins = {}
plugins_periodic = {}


def load_modules(_callback=None, *args, **kwargs):
    """
    Dynamically load new modules in the plugins directory.
    The module has to be loaded as a separate directory and have a __init__.py file.
    """

    logger.debug("load_modules: args: {}, kwargs: {}".format(args, kwargs))

    import os

    lst = os.listdir('./core/plugins')
    dir = []
    for d in lst:
        s = os.path.abspath('./core/plugins') + os.sep + d
        if os.path.isdir(s) and os.path.exists(s + os.sep + '__init__.py'):
            dir.append(d)

    if len(plugins) > 0:
        remove_modules(plugins, dir)

    for d in dir:
        if d not in plugins:
            plugins[d] = importlib.import_module('plugins.' + d + '.' + d)

    if _callback:
        _callback()


def remove_modules(lst1, lst2):
    """
    Remove the difference between modules found and current state of modules
    """
    res = list(set(lst1) - set(lst2))

    logger.debug('remove_modules(): res:{}'.format(res))

    for key in res:
        try:
            plugins.pop(key)
            plugins_periodic.get(key).stop()
            plugins_periodic.pop(key)

            ActionProvider.plugins = [plugin for plugin in ActionProvider.plugins if str(
                plugin.__name__).lower() != key]
            sys.modules.pop('plugins.'+key+'.'+key)
        except KeyError as ke:
            logger.debug(ke)


def perform_modules():
    logger.debug('perform_modules(): plugins:{}'.format(
        ActionProvider.plugins))

    for action in ActionProvider.plugins:
        module_name = str(action.__module__).split(".")[-1]
        if module_name not in plugins_periodic:
            plugins_periodic[module_name] = Periodic(
                5, action().perform, None, kwargs={'autostart': True})


class Periodic(object):
    """
    A periodic task running in threading.Timers
    """

    def __init__(self, interval, function, callback, *args, **kwargs):
        self._lock = Lock()
        self._timer = None
        self.function = function
        self.callback = callback
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self._stopped = True
        if kwargs.pop('autostart', True):
            self.start()

    def start(self, from_run=False):
        logger.debug("Periodic::start(): function:{}".format(self.function))

        self._lock.acquire()
        if from_run or self._stopped:
            self._stopped = False
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self._lock.release()

    def _run(self):
        logger.debug("Periodic::_run(): function:{}".format(self.function))

        self.start(from_run=True)
        if self.callback:
            self.function(self.callback, *self.args, **self.kwargs)
        else:
            self.function(*self.args, **self.kwargs)

    def stop(self):
        logger.debug("Periodic::stop()")

        self._lock.acquire()
        self._stopped = True
        self._timer.cancel()
        self._lock.release()


if __name__ == '__main__':

    # First call is needed before making it run periodically
    load_modules(perform_modules)
    lm_periodic = Periodic(
        5, load_modules, perform_modules, kwargs={'autostart': True})

    # # TODO need to make the for loop execute when new modules are imported, and
    # # only Periodic for new modules must be bade
    # try:
    #     for action in ActionProvider.plugins:
    #         action_periodic = Periodic(
    #             1, action().perform, kwargs={'autostart': True})

    # finally:
    #     lm_periodic.stop()
