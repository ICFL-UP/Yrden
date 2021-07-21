import importlib
import logging
from action_provider import ActionProvider

from threading import Timer, Lock
from time import sleep

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('main')


def load_modules(*args, **kwargs):
    """
    Dynamically load new modules in the plugins directory.
    The module has to be loaded as a separate directory and have a __init__.py file.
    """

    logger.debug("load_modules: args: {}, kwargs: {}".format(args, kwargs))

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

    print(res)
    return res


class Periodic(object):
    """
    A periodic task running in threading.Timers
    """

    def __init__(self, interval, function, *args, **kwargs):
        self._lock = Lock()
        self._timer = None
        self.function = function
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self._stopped = True
        if kwargs.pop('autostart', True):
            self.start()

    def start(self, from_run=False):
        logger.debug("Periodic::start(): function:{}, interval:{}, args:{}, kwargs:{}".format(
            self.function, self.interval, self.args, self.kwargs))

        self._lock.acquire()
        if from_run or self._stopped:
            self._stopped = False
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self._lock.release()

    def _run(self):
        logger.debug("Periodic::_run(): function:{}, interval:{}, args:{}, kwargs:{}".format(
            self.function, self.interval, self.args, self.kwargs))

        self.start(from_run=True)
        self.function(*self.args, **self.kwargs)

    def stop(self):
        logger.debug("Periodic::stop()")

        self._lock.acquire()
        self._stopped = True
        self._timer.cancel()
        self._lock.release()


if __name__ == '__main__':

    load_modules()  # First call is needed before making it run periodically
    lm_periodic = Periodic(10, load_modules, kwargs={'autostart': True})

    # TODO need to make the for loop execute when new modules are imported, and
    # only Periodic for new modules must be bade
    try:
        for action in ActionProvider.plugins:
            action_periodic = Periodic(
                1, action().perform, kwargs={'autostart': True})

    finally:
        lm_periodic.stop()
