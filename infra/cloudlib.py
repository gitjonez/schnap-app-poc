import sys
import yaml
from typing import Dict, Any, Union
from boto3 import Session, resource
from botocore.exceptions import ClientError

Config = Dict[str, Any]

CONF_FILE: str = 'configuration.yml'


class Configuration:
    '''yaml loader'''

    def __init__(self, conf_file: str = CONF_FILE):
        '''Load cloud configuration into: self.config'''
        self._conf_file: str = conf_file
        self.config: Config = {}

        try:
            with open(conf_file) as fh:
                self.config = yaml.load(fh, Loader=yaml.SafeLoader)
        except FileNotFoundError as e:
            print(f'ERROR: Configuration file "{conf_file}" not found',
                  file=sys.stderr)

        self.aws_profile: str = self.config['aws_profile']


class Aws:
    '''Aws Helper'''

    def __init__(self, profile: str):
        self.profile_name = profile
        self.session = Session(profile_name=profile)
        self.ec2_resource = self.session.resource('ec2')


class Network:
    '''Network Helper'''

    def __init__(self, config: Config, ec2: resource):
        self.config: Config = config
        self.ec2: resource = ec2
        self.vpc: resource = None

    def __str__(self):
        '''Represent self as a string for:
           print(net), for example. 
        '''
        # build a dict
        kv = {'ec2': self.ec2}
        kv['config_vpc_cidr'] = self.config['vpc_cidr']
        kv['vpc'] = self.vpc

        # key=value list
        params: list = []
        for k, v in kv.items():
            params.append(f'{k}={v}')

        # build string
        s = f'Network({", ".join(params)})'
        return s

    def add_vpc(self, vpc_cidr: str):
        try:
            self.vpc = self.ec2.create_vpc(CidrBlock=vpc_cidr)
        except ClientError as e:
            print(f'Create VPC error: {str(e)}', file=sys.stderr)

    def delete_vpc(self):

        def delete_error(e: Exception):
            print(f'Delete VPC error: {e}', file=sys.stderr)
            print(f'  VPC: {self.vpc}', file=sys.stderr)

        try:
            response = self.vpc.delete()
            http_status = response['ResponseMetadata']['HTTPStatusCode']
            if http_status != 200:
                raise ClientError(f'Status not OK ({http_status})')
        except ClientError as e:
            delete_error(e)

        self.vpc = None


if __name__ == '__main__':
    # test code
    c = Configuration(f'../{CONF_FILE}')
    cloud = Aws(c.config['aws_profile'])
    net = Network(c.config['network'], cloud.ec2_resource)
    vpc_cidr: str = net.config['vpc_cidr']

    print(f'Create VPC: {vpc_cidr}')
    net.add_vpc(vpc_cidr)

    print(net)
    #print('Network:')
    #print(f'  Vpc resource: {net.vpc}')
    #print(f'    Id: {net.vpc.id}')
    #print(f'  Cidr: {net.vpc.cidr_block}')

    print(f'Delete VPC: {vpc_cidr}:{net.vpc.id}')
    net.delete_vpc()
