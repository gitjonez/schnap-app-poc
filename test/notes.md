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
