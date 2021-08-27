from enum import Enum


class PluginStatus(Enum):
    VIRTUALENV = 'Creating virtual environment'
    DEPENDECIES = 'Installing dependencies'
    SUCCESS = 'Success'
    Failed = 'Failed'
