import sys
import boto3

ses: boto3.Session = None
ec2: boto3.resource = None
region: str = ''


def usage():
    print('taste [-h] aws_profile ami-id')
    sys.exit()


def connect(aws_profile: str):
    global ses
    global ec2
    global region
    ses = boto3.Session(profile_name=aws_profile)
    region = ses.region_name
    ec2 = ses.resource('ec2')


def describe_instances(ami: str = '') -> list:
    '''Return instance ids. If ami is passed, if it's already running
        (we don't have to start an instance) return list of instances
    '''
    instances: list = []
    for instance in ec2.instances.all():
        if ami:
            if (instance.image_id == ami
                    and instance.state['Value'] == 'running'):
                instances.append(instance.id)
        else:
            instances.append(instance.id)
    return instances


def find_image(ami: str) -> bool:
    '''Return True if AMI is found'''
    images = ec2.images.filter(Filters=[{
        'Name': 'is-public',
        'Values': ['false']
    }],
                               ImageIds=[ami])  # thanks yapf :/
    if images:
        return True
    else:
        return False


def run_instance(ami_id,
                 instance_type: str = 't2.micro',
                 avzone: str = 'c') -> dict:
    '''Run instance.
        (avzone (char[1]) means `region{avzone}`) '''
    pass


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
        print(f'AMI {ami_id} not found.')
        sys.exit()

    running = False
    instances = describe_instances(ami_id)
    if instances:
        running = True
        print(f'Image {ami_id} is already running. Instance Ids:')
        print('\n'.join(instances))
    else:
        print(f'Launching instance from {ami_id}...')
        instance_id = run_instance(ami_id)
