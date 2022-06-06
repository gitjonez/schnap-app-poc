# schnap-app-poc 
Sample AWS Project

Doodling with AWS ELB using EC2 for a zero downtime upgrade.
(was: repo: dennis-mahle)

## Table of Contents
- Architecture
- Web Service
- Prerequisites
- Executing the Upgrade

## Architecture
I've set up a very simple "website" with a classic setup in AWS cloud. 
The general rule I followed was "expose as little as possible"

### "Hostname.DomainName" in DNS (route53)
*schnap.jonez.tech* in this case

### AWS VPC in the "us-west-2" Region, accross 2 Availability Zones (AZ)
- **schnap-app-vpc** ` vpc-0f1189ea189a60331 10.2.0.0/16`
Subnets:
```
schnap-app-subnet-public1-us-west-2a	us-west-2a	10.2.0.0/20
schnap-app-subnet-private2-us-west-2b	us-west-2b	10.2.144.0/20
schnap-app-subnet-public2-us-west-2b	us-west-2b	10.2.16.0/20
schnap-app-subnet-private1-us-west-2a	us-west-2a	10.2.128.0/20
```
- There's a lot more going on if we dig deeper, with Route Tables, ACL, Gateways, etcetera which I'll spare you the bordom except for saying "things should be as simple as possible" and a quote attributed to pioneering computer scientist Donald Knuth: "Premature Optimization is the root of all evil." (*edit: to a degree. It depends)

### Web Servers
- The actual "web servers" are placed on private subnets at least one per AZ
- Amazon Linux 2 instances with a custom webserver listening on port 8080. The service is configured as a `systemd` service which starts on boot and runs as a non-privilidged user. 
- Builds of the service are set-up as Amazon Machine Instances (AMI) for ease and speed of bringing up nodes at registering them to a "Target Group". 

### Load Balancer (ELB/ALB)
- Listeners on each public subnet, forwarding requests to web servers on private subnets
- The newer EC2 and ELB services have Target Groups. Groups are set up with a common configuration. For example, the service port and health URL are common to the target group. When targets are added to the group, they assume these properties. 

*While all the architecture (infrastructure) can be created completely with automation, this code is still in progress (see `infra/cloudlib.py`)

## Web Service
- The service is a tutorial for a (very) simple "wiki" site. What it does is mostly irrelevant to this exercise. 
- Health check: services or service groups have a custom context which load balancers or other orchestration can get service health for scaling or removing from service
- This health check is extremely simple: if successful, returns the version of the service and system datetime. (HTTP 200)
- For "reasons", I went with a custom web server/web app written in the Go programming language, leveraging the standard library "net/http" package. 
- See: `src/schnap/schnap.go`
- and service definition: `src/schnap/schnap.service`


## Prerequisites

### Infra and Application started and operational
This POC primarily demonstrates the hot upgrade. Some work was done to "rewrite terraform" but, zero downtime upgrade was the priority

### Account - IAM user configured
`~/.aws/config` (accounts, access keys)

### SSH Key pair
Best to cut a new key, they're cheap:
- `ssh-keygen -C schnap-rsa -b 4069`
- The ssh key pair is for configuring build hosts (or bastion host if you need one)
- Best practice, not for service hosts, nodes, etc. It shouldn't be necessary and poses risk. 
```
aws ec2 import-key-pair  \
  --profile <aws-profile-name> \ 
  --key-name <key-name>-rsa  \
  --public-key-material fileb://~/.ssh/<key-name>-rsa.pub 
```

### Python
The hot upgrade tools have been developed with Python. Yeah, we probably could/should containerize this but for now,  we need the proper python and python environment.
 - python >= 3.7 (tested with python 3.9)
 - boto3
 - yaml (for the incomplete `cloudlib.py`, yamo based configuration)
 
A python runtime is beyond the scope of this document but basically, with your favorite python env manager, create a new "pyenv" (python=3.9) and install `boto3` and `pyyaml`.
If there were smoke tests, we'd run those to check compilation and link. It would probably be wise to test new CI/CD tools on a dev/stage enviroment before having at it "in real life", PROD, or whatever you want to call it  =)

## Performing the upgrade
### Test Client
There's a simple test client: `test/client.py`
Quick and dirty, multithreaded client which tracks health through the load balancer: Cumulative stats of:
- Reported Versions (and counts)
- HTTP status codes (and counts)
Just run the python script: it fires off 20 requests and sleeps for a short period of time and continues until ^C or other process interruption. 
Example: 
```
shell$ cd test/
shell$ python client.py
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
```
Spoiler alert: this is how we're testing the upgrade. 

## Executing the upgrade
`cd test && taste.py aws_profile ami_id`

We'll "taste" a new app server version by bring up a new node with the new version. As explained above: This AMI needs to be pre-built and ready to launch. 

Spoiler alert: we didn't get past the tasting and and automated backout or "GO" to upgrade all the nodes but we're 90% there. 
The `taste` code will be modularized and included by the (TBD) `upgrade` code with backout capabilities. 
So, upgrade would be: 
- taste
- test
- analyze health
- prompt engineer (at first) to GO/NO-GO. 
- If GO:
  - The missing link, after one taste is to launch instances of the new AMIs, and register them with the Target Group(s) which the LB is forwarding to.  
  - Monitor health (with client.py, automatically)
  - Deregister replaced Instances
  - Monitor health
  - Stop replaced instances
  - Monitor health
  - (eventually) Terminate replaced instances
  - (eventually) Deregister old AMIs
  - (eventually) Continue the automation regime – extend and maintain the CI/CD

### Step-by-step
- Clone this repo
- Prepare the prerequisites 
- Verify the app with `client.py`
- [re]start `client.py`
- Taste the new image ("run the script")
  - `cd test`
  - `python taste.py AWS_PROFILE_NAME AMI_IMAGE`
- Monitor output of both modules

### Actual output:
*taste.py*
```
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
```
*client.py* (simultaneously)
```
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
```

*NB for cost reasons, the site is turned off at the moment*

You made it to the end! Congrats!
