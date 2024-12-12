from .log_prep import config as logconf
from .singleton import Singleton

from bshlib.utils import super_touch
from pathlib import Path
from loguru import logger
import tomlkit
import os

logconf()

class Configuration(metaclass=Singleton):
    """
    Configuration for a project.

    For accesing and modifying the config object, use the `Configuration.map` attribute.

    Its implementation of a singleton prohibits multiple configurations for different projects to exist simultaneously.
    """

    _run_stat: dict
    """Runtime status, mostly flags"""
    _stgfile: Path
    """Settings file path"""
    project: str
    """Project name"""
    map: tomlkit.TOMLDocument
    """Settings object"""

    def __init__(self, project: str):
        self._run_stat = {'did_init': False}
        self._stgfile = Path(os.environ["HOME"]) / '.config' / project / 'settings.toml'
        self.project = project
        # TODO: dont debug log anything unless initialized with a option `debug=True`
        logger.debug('parsing settings file..')
        self.map = self.__parse()
        if self._run_stat['did_init']:
            self.save()

    def __parse(self):
        """
        Parse settings from file.

        Will create and initialize file if not found.
        """
        try:
            with open(self._stgfile, 'rt') as f:
                stg = tomlkit.load(f)
            logger.success('settings applied')
        except FileNotFoundError:
            super_touch(self._stgfile)
            stg = tomlkit.document()
            stg.add(tomlkit.comment(f'{self.project} configuration'))
            stg.add(tomlkit.nl())
            logger.success('settings initialized')
            self._run_stat['did_init'] = True
        return stg

    def save(self):
        with open(self._stgfile, 'wt') as f:
            tomlkit.dump(self.map, f)
        logger.success('settings saved')
