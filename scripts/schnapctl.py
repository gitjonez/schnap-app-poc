#!/usr/bin/env python3
import sys
from boto3 import Session, resource, client
from botocore.exceptions import ClientError

APP_NAME = 'schnap'
AWS_PROFILE = 'dennis.mahle'
ses: Session = None
ec2: resource = None
elbv2: client = None


def usage():
    text = 'schnapctl [-h] <command>\n'
    text += '  commands:\n'
    text += '     up:       bring UP app, start all instances, load balancer\n'
    text += '   down:       bring DOWN all instances, load balancer\n'
    print(text)
    sys.exit()


def connect():
    global ses
    global ec2
    global elbv2
    ses = Session(profile_name=AWS_PROFILE)
    ec2 = ses.resource('ec2')
    elbv2 = ses.client('elbv2')


def stop_all_instances():
    instances: list = list(ec2.instances.all())
    j = 0 
    for i, inst in enumerate(instances):
        if inst.state['Name'] in ['running', 'pending']:
            inst.stop()
            print(f'{i}: stopped {inst.id}')
    if i >= 0:
        print(f'Instances stopped.')


def delete_load_balancer():
    lb_resp = elbv2.describe_load_balancers()
    load_balancers = lb_resp['LoadBalancers']
    if load_balancers:
        for lb in load_balancers:
            if lb['LoadBalancerName'].startswith(APP_NAME):
                arn = lb['LoadBalancerArn']
                del_lb = elbv2.delete_load_balancer(LoadBalancerArn=arn)
                print(f'LB deleted: {lb["LoadBalancerName"]}')


def app_down():
    stop_all_instances()
    delete_load_balancer()


if __name__ == '__main__':
    argi: int = 0
    argc: int = len(sys.argv)
    if argc < 2 or argc > 3 or sys.argv[1] == '-h':
        usage()
    if sys.argv[1] != 'up' and sys.argv[1] != 'down':
        usage()

    connect()
    if sys.argv[1] == 'down':
        app_down()

'''
{'LoadBalancerArn': 'arn:aws:elasticloadbalancing:us-west-2:864095940680:loadbalancer/app/schnap-app/9049f6a019a875f3',
  'DNSName': 'schnap-app-2115484130.us-west-2.elb.amazonaws.com',
  'CanonicalHostedZoneId': 'Z1H1FL5HABSF5',
  'CreatedTime': datetime.datetime(2022, 6, 5, 0, 40, 19, 160000, tzinfo=tzutc()),
  'LoadBalancerName': 'schnap-app',
  'Scheme': 'internet-facing',
  'VpcId': 'vpc-0f1189ea189a60331',
  'State': {'Code': 'active'},
  'Type': 'application',
  'AvailabilityZones': [{'ZoneName': 'us-west-2a',
    'SubnetId': 'subnet-0374bbf0c76403d66',
    'LoadBalancerAddresses': []},
   {'ZoneName': 'us-west-2b',
    'SubnetId': 'subnet-0d40f652618a7769c',
    'LoadBalancerAddresses': []}],
  'SecurityGroups': ['sg-05d0747fe6c723cb3'],
  'IpAddressType': 'ipv4'}
'''