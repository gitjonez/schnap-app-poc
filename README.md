# dennis-mahle
Sample AWS Project

Doodling with AWS ELB using EC2 for a zero downtime upgrade.

## Table of Contents
- Architecture
- Service

## Architecture
I've set up a very simple "website" with a classic setup in AWS cloud. 
The general rule I followed was "expose as little as possible"
- "Hostname.DomainName" in DNS (route53)
  - *schnap.jonez.tech* in this case
- AWS VPC in the "us-west-2" Region, accross 2 Availability Zones (AZ)
 - **schnap-app-vpc** ` vpc-0f1189ea189a60331 10.2.0.0/16`
 - Subnets:
```
schnap-app-subnet-public1-us-west-2a	us-west-2a	10.2.0.0/20
schnap-app-subnet-private2-us-west-2b	us-west-2b	10.2.144.0/20
schnap-app-subnet-public2-us-west-2b	us-west-2b	10.2.16.0/20
schnap-app-subnet-private1-us-west-2a	us-west-2a	10.2.128.0/20
```
  - There's a lot more going on if we dig deeper, with Route Tables, ACL, Gateways, etcetera which I'll spare you the bordom except for saying "things should be as simple as possible" and a quote attributed to pioneering computer scientist Donald Knuth: "Premature Optimization is the root of all evil." 
- Web Servers
  - The actual "web servers" are placed on private subnets at least one per AZ
  - Amazon Linux 2 instances with a custom webserver listening on port 8080. The service is configured as a `systemd` service which starts on boot and runs as a non-privilidged user. 
  - Builds of the service are set-up as Amazon Machine Instances (AMI) for ease and speed of bringing up nodes at registering them to a "Target Group". 
- Load Balancer (ELB/ALB)
  - Listeners on each public subnet, forwarding requests to web servers on private subnets
  - The newer EC2 and ELB services have Target Groups. Groups are set up with a common configuration. For example, the service port and health URL are common to the target group. When targets are added to the group, they assume these properties. 
- *While all the architecture (infrastructure) can be created completely with automation, this code is still in progress (see `infra/cloudlib.py`)

## Web Service
- The service is a tutorial for a (very) simple "wiki" site. What it does is mostly irrelevant to this exercise. 
- Health check: services or service groups have a custom context which load balancers or other orchestration can get service health for scaling or removing from service
- This health check is extremely simple: if successful, returns the version of the service and system datetime. (HTTP 200)
- For "reasons", I went with a custom web server/web app written in the Go programming language, leveraging the standard library "net/http" package. 
- See: `src/schnap/schnap.go`


## Prerequisites
- 2 AZ VPC: pub/priv subnet on each
- 2 AMIs: current service + upgraded service
- 2 Running instances, one on each 
- 

### Account - IAM user - `~/.aws/config` stuff
- I've picked a project name `schnap`
  - Used below for various names


### SSH Key pair
- Best to cut a new key, they're cheap:
- `ssh-keygen -C schnap-rsa -b 4069`

```
aws ec2 import-key-pair  \
  --profile <aws-profile-name> \ 
  --key-name <key-name>-rsa  \
  --public-key-material fileb://~/.ssh/<key-name>-rsa.pub 
```
### Python
Yeah, we probably can just Dockerize this but for now we need packages: 
- python >= 3.10 (likely python >= 3.7)
- boto3
- yaml
