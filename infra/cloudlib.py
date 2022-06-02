import sys
import yaml
from typing import Union, Dict
from boto3 import Session

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
        self.session = Session(profile_name=profile)

class Network:
    '''Network Helper
    '''
    def __init__(self, config: Config, session: Session): 
        self.session = session

class Vpc:
    '''Vpc helper
    '''
    def __init__(self, config: Config):
        self.vpc_config: Config = config

class Dns:
    pass



if __name__ == '__main__':
    # conf = Configuration()
    conf = Configuration(f'../{CONF_FILE}')
    # print(conf.config)
