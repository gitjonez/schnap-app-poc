InvalidTargetException

```
❯ aws ec2 describe-instances --profile dennis.mahle \
  | jq -r '.Reservations[].Instances[] | [.ImageId, .InstanceId, .Placement.AvailabilityZone, .Tags[0].Value] | @tsv '
ami-01be087946c03b82c	i-0c56aa1266cfd38ff	us-west-2b	schnap-b
ami-0f333223621ac4172	i-0d8548befdc7be5a7	us-west-2b	taste-test
ami-01be087946c03b82c	i-023758dc78d992c7f	us-west-2a	schnap-a
```

### schnapctl
❯ schnapctl down
0: stopped i-0c56aa1266cfd38ff
1: stopped i-0d8548befdc7be5a7
2: stopped i-023758dc78d992c7f
Instances stopped.
LB deleted: schnap

❯ ipython taste.py dennis.mahle ami-0f333223621ac4172
Launching instance from ami-0f333223621ac4172 ...
subnet: subnet-0bd5b40edeb31d44f
security group: sg-02fbcf414c3764d5b
Instance i-0d8548befdc7be5a7 launched ...
Instance launched...
Checking target group...
target_grp_arn: arn:aws:elasticloadbalancing:us-west-2:864095940680:targetgroup/schnap/a7218432cb73f883
Waiting for instance to enter "running" state...
Register target...
We cool? Cool!

IMAGE SETUP
manual
yum install git golang
install schnap.service
ssh identity setup
add user
git clone <ssh-link>
go build ~/.../schnap.go
chmod ... ec2_user
test/verify service (elinks)
Create AMI

Create new build (new version) update the code on the builder instance
Create AMI

Start v1 of the AMIs 
Add instances to TargetGroup

Create load balancer; configure, test with client.py

❯ ipython client.py
Starting load to: http://schnap.jonez.tech/health/
statuses:
 200: 20
versions:
 0.1.5: 20

statuses:
 200: 40
versions:
 0.1.5: 40

statuses:
 200: 60
versions:
 0.1.5: 60

statuses:
 200: 80
versions:
 0.1.5: 80

statuses:
 200: 100
versions:
 0.1.5: 100

statuses:
 200: 120
versions:
 0.1.5: 120

statuses:
 200: 140
versions:
 0.1.5: 140

statuses:
 200: 160
versions:
 0.1.5: 160

statuses:
 200: 180
versions:
 0.1.5: 173 0.1.6: 7

statuses:
 200: 200
versions:
 0.1.5: 187 0.1.6: 13

statuses:
 200: 220
versions:
 0.1.5: 200 0.1.6: 20

^C---------------------------------------------------------------------------
KeyboardInterrupt