# dennis-mahle
Sample AWS Project

## Outline
- src/schnap:  *Sample "webapp"*
- Bring up services
  - VPC
  - CLB
  - App
  - Domain
  - Data
- Deploy Update

## Requirements

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
