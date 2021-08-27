from enum import Enum


class RunStatus(Enum):
    FAILED = 'Failed'
    HASH_FAILED = 'Hash Failed'
    SUCCESS = 'Success'
    TIMED_OUT = 'Timed Out'
