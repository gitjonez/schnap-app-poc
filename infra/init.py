import sys
import yaml
import boto3
from typing import Union, Dict

Entry = Union[str, dict]
Config = Union[Entry, None]

CONF_FILE: str = 'configuration.yml'


class Configuration:

    def __init__(self, conf_file: str = CONF_FILE):
        '''Load cloud configuration into: self.config
        '''
        self._conf_file: str = conf_file
        self.config: Config = None

        try:
            with open(conf_file) as fh:
                self.config = yaml.load(fh, Loader=yaml.SafeLoader)
        except FileNotFoundError as e:
            print(f'ERROR: Configuration file "{conf_file}" not found',
                  file=sys.stderr)

class Aws:
    '''Aws Helper
    '''
    def __init__(self, profile):
        self.profile_name = profile
        self.session = boto3.Session(profile_name=profile)

class Dns:
    pass


if __name__ == '__main__':
    # conf = Configuration()
    conf = Configuration(f'../{CONF_FILE}')
    # print(conf.config)
