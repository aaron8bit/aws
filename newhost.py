import boto, boto.ec2, time, os
from boto.vpc import VPCConnection

access_key    = os.environ['AWS_ACCESS_KEY']
secret_key    = os.environ['AWS_SECRET_ACCESS_KEY']
keypair_name  = 'AJA-Key'

###########################################################
# Script to pass to AWS to run at launch
############################################################
user_data = """#!/bin/bash
yum update -y
touch /thisworked
  """

###########################################################
# Set the region
############################################################
set_region = boto.ec2.get_region('us-east-1')


###########################################################
# Create a connection to EC2
# Verify key pair already exists, if not, create a new one
############################################################
conn  = boto.connect_ec2(access_key, secret_key, region=set_region)
try:
  key   = conn.create_key_pair(keypair_name)
  key.save("./")
except:
  True # Key already created

###########################################################
# Some test code on creating security groups, not needed right now
###########################################################
#group_name = "AJA Salt Group"
#try:
#  groups = [g for g in conn.get_all_security_groups() if g.name == group_name]
#  group = groups[0] if groups else None
#  if not group:
#    group = conn.create_security_group(group_name, "A group for %s"%(group_name,))
#  group.authorize(ip_protocol='tcp',
#                  from_port=str(22),
#                  to_port=str(22),
#                  cidr_ip='0.0.0.0/0')
#  group.authorize(ip_protocol='tcp',
#                  from_port=str(80),
#                  to_port=str(80),
#                  cidr_ip='0.0.0.0/0')
#except:
#  True

###########################################################
# Specify a specific network in a custom VPC, assigned a 
# public IP and a default security group
###########################################################
interface = boto.ec2.networkinterface.NetworkInterfaceSpecification(subnet_id='subnet-0726ac71',
                                                                    groups=['sg-4389213b'],
                                                                    associate_public_ip_address=True)
interfaces = boto.ec2.networkinterface.NetworkInterfaceCollection(interface)

# This AMI is for Ubuntu
#reservation = conn.run_instances(image_id='ami-fce3c696',

# This AMI is for Amazon Linux
#reservation = conn.run_instances(image_id='ami-8fcee4e5',

###########################################################
# Launch a new instance
###########################################################
reservation = conn.run_instances(image_id='ami-8fcee4e5',
                                 instance_type='t2.micro',
                                 key_name=keypair_name,
                                 network_interfaces=interfaces,
                                 user_data=user_data)

###########################################################
# get the instance, wait until running
###########################################################
running_instance = reservation.instances[0]
status = running_instance.update()
while status == 'pending':
    time.sleep(10)
    status = running_instance.update()
print(running_instance.ip_address)

###########################################################
# Define a tage for names, intended for reuse later
# Figure out a better way to do this
###########################################################
def nTag(what):
    return {'Name': 'AJA ' + str(what)}

###########################################################
# Set Name
# Set Security Group
###########################################################
if status == 'running':
    running_instance.add_tags(nTag("New Server"))
    # Security group is being set with the interface right now
    #running_instance.modify_attribute('groupSet', ["sg-4389213b"])
else:
    print('Instance status: ' + status)



