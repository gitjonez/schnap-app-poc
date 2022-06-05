import sys
import boto3
from boto3 import resource
from botocore.exceptions import ClientError

# globals / CONSTANTS
ses: boto3.Session = None
ec2: boto3.resource = None
elbv2: boto3.client = None
region: str = ''
owner_id: str = ''

INSTANCE_TYPE = 't2.micro'
KEY_PAIR = 'schnap-rsa'
PROJECT_NAME = 'schnap'
PRIVATE_SUBNET = 'private-traffic'


def usage():
    print('taste [-h] aws_profile ami-id')
    sys.exit()


def connect(aws_profile: str):
    global ses
    global ec2
    global elbv2
    global region
    global owner_id
    ses = boto3.Session(profile_name=aws_profile)
    region = ses.region_name
    ec2 = ses.resource('ec2')
    sts = ses.client('sts')
    elbv2 = ses.client('elbv2')
    owner_id = sts.get_caller_identity()['Account']


def describe_instances(ami: str = '') -> list:
    '''Return instance ids. If ami is passed, if it's already running
        (we don't have to start an instance) return list of instances
    '''
    instances: list = []
    for instance in ec2.instances.all():
        if ami:
            state = instance.state
            if (instance.image_id == ami and
                (state['Name'] == 'running' or state['Name'] == 'pending')):
                instances.append(instance.id)
        else:
            instances.append(instance.id)
    return instances


def find_image(ami: str) -> bool:
    '''Return True if AMI is found'''
    try:
        images = list(ec2.images.filter(Owners=[owner_id], ImageIds=[ami]))
    except ClientError as e:
        print(f"* D'oh!:\n  {e}")
        return False
    if images:
        return True
    else:
        return False


def get_security_group() -> str:
    '''Find security group by configured name
       Return "group_id" '''
    return list(
        ec2.security_groups.filter(Filters=[{
            'Name': 'group-name',
            'Values': [PRIVATE_SUBNET]
        }]))[0].group_id


def get_subnet_res(avzone: str, filter: str = 'private') -> list:
    '''Return list(resources)  One or none
        (assumes only one tag: Name) '''
    zone = f'{region}{avzone}'
    print(f'zone = {zone}')
    subnets = list(ec2.subnets.all())
    matches = []
    for sn in subnets:
        name = sn.tags[0]['Value']
        if filter in name and name.endswith(zone):
            matches.append(sn)
    if len(matches) != 1:
        return []
    return matches


def run_instance_helper(ami: str,
                        subnet: str,
                        group_id: str,
                        name_tag='taste-test',
                        instance_type=INSTANCE_TYPE,
                        key_name=KEY_PAIR) -> resource:
    try:
        instances: list = ec2.create_instances(ImageId=ami,
                                               InstanceType=instance_type,
                                               KeyName=key_name,
                                               SubnetId=subnet,
                                               SecurityGroupIds=[group_id],
                                               MaxCount=1,
                                               MinCount=1,
                                               TagSpecifications=[{
                                                   'ResourceType':
                                                   'instance',
                                                   'Tags': [{
                                                       'Key': 'Name',
                                                       'Value': name_tag
                                                   }]
                                               }])
    except ClientError as e:
        print(f"* D'oh!\n  {e}")
        sys.exit(1)

    instance: resource = instances[0]
    print(f'Instance {instance.id} launched ...')
    return instance


def run_instance(ami_id,
                 instance_type: str = 't2.micro',
                 avzone: str = 'b') -> str:
    '''Run instance in from AMI in private subnet.
        Assume: security group named "private-traffic".
        (avzone (char[1]) means `region{avzone}`) '''
    subnet = get_subnet_res(avzone='b')
    if not subnet:
        print(f"Can't find subnet for AZ {region}{avzone}")
    subnet_id = subnet[0].id
    group_id = get_security_group()
    print(f'subnet: {subnet_id}')
    print(f'security group: {group_id}')
    instance: resource = run_instance_helper(ami=ami_id,
                                             subnet=subnet_id,
                                             group_id=group_id)

    return instance.id


def get_target_group_arn(name=PROJECT_NAME) -> str:
    resp: dict = elbv2.describe_target_groups(Names=[PROJECT_NAME])
    tg: dict = resp['TargetGroups'][0]
    return tg['TargetGroupArn']


if __name__ == '__main__':
    args = sys.argv.copy()
    if '-h' in args:
        usage()
    argc = len(args)
    if argc != 3:
        usage()

    aws_profile = args[1]
    ami_id = args[2]
    connect(aws_profile)

    if not find_image(ami_id):
        print(f'AMI "{ami_id}" not found.')
        sys.exit()

    running = False
    instances = describe_instances(ami_id)
    if instances:
        running = True
        print(f'Image {ami_id} is already running. Instance Ids:')
        print('  {}'.format("\n".join(instances)))
    else:
        print(f'Launching instance from {ami_id} ...')
        instance_id = run_instance(ami_id)
    print(f'Instance launched...')
    target_grp_arn = get_target_group_arn()
    print(f'target_grp_arn: {target_grp_arn}')
