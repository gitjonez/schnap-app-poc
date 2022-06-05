# dennis-mahle
Sample AWS Project

Doodling with AWS ELB using EC2 for a zero downtime upgrade.

## Table of Contents
- Architecture

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
- Load Balancer (ELB/ALB)
  - Listeners on each public subnet, forwarding requests to web servers on private subnets. 

#### attic
- src/schnap:  *Sample "webapp"*
- Bring up services
  - VPC
  - CLB
  - App
  - Domain
  - Data
- Deploy Update

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
