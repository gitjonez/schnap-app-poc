import boto3

ses = boto3.Session(profile_name='dennis.mahle')
dns = ses.client(session=ses)

# route53

jzone = dns.get_hosted_zone(
    Id='/hostedzone/Z31SPCHSIDXAKK')['HostedZone']['Id']

recs = dns.list_resource_record_sets(HostedZoneId=jzone)
for r in recs:
    if r['Type'] == 'A' and r['Name'].startswith('offnet.jonez'):
        target = r
offnet = target

change_req = {
    'HostedZoneId': jzone,
    'ChangeBatch': {
        'Comment': 'Change offnet TTL',
        'Changes': [{
            'Action': 'UPSERT',
            'ResourceRecordSet': offnet
        }]
    }
}

_ = dns.change_resource_record_sets(HostedZoneId=jzone,
                                    ChangeBatch=change_req['ChangeBatch'])

ec2cli = ses.client('ec2')
response = ec2cli.describe_images(Filters=[{
    'Name':
    'description',
    'Values': ['Amazon Linux 2 Kernel 5.10 AMI 2.0.20220426.0 x86_64 HVM gp2']
}, {
    'Name': 'is-public',
    'Values': ['true']
}])

