#!/usr/env python
import datetime
import json
def init_bash():

	'''
	This function will generate a a bash script to run when the
	AWS spot instance is initalized

	The commands below are for a Ubuntu/Debian (I think) image. The directories for your image
	might differ from the ones below
	'''
	commands=[ 
		'#!/bin/bash',
		'apt-get update -y',
		'apt-get install awscli -y',
		'mount /dev/xvdb /home/admin/data',
		'chmod 777 /home/admin','chmod 777 /home/admin/data',
		'rm -rf /home/admin/data/*',
		
		# The wget command moves a config file from S3 to the instance
		# This config file contains the AWS CLI user credentials used for uploading results to S3 buckets
		# 'wget https://s3.amazonaws.com/1kg-gtcnv/config -T 10 -t 5 -O /home/admin/config',
		# 'mv /home/admin/config /home/admin/.aws/', # .aws is the config file for AWS CLI
		
		# The binaries below were saved in a Linux image we created for our analysis
		# 'export PATH=/home/admin/bin/bedtools2/bin:$PATH',
		# 'export PATH=/home/admin/bin/samtools-1.2:$PATH'
		 ]
	return '\n'.join(commands).encode('base64') # The init commands must be encoded in base64
def init_json(base64_command,out):
	'''
	Input: output from init_bash(), outfile name
	
	This function creats a JSON file containing information for initalizing an AWS instance 
	
	You will have to edit some of the values for your AWS acount
	'''
	ofh = open(out+'.json','w') 
	json_out= {
		'ImageId': 'YOUR_AWS_IMAGE_ID', #'ImageId': 'ami-8d3164e7',
		'KeyName': 'YOUR_AWS_KEY', #'KeyName': '1kg_test',
		'SecurityGroups': ['YOUR_AWS_GROUPS'],  #'SecurityGroups': ['gtcnv'], This is a list apparently 
		'UserData': base64_command,
		'InstanceType': 'm4.xlarge' # Here you can select which type of instance to spawn 
		}
	ofh.write(json.dumps(json_out,indent=4,separators=(',',': '))+'\n')
	ofh.close() 
def init_command(out,price):
	'''
	Input: outfile name, [FLOAT] price for spot market instance

	This function creates a local Bash script to spawn AWS instances with the AWS CLI

	It's required to have the outfile name to be the same as the outfile name for init_json() 
	'''
	ofh = open(out+'.sh','w')
	# The AWS instance request will be active for 25 hours from the current time
	timestamp = datetime.datetime.utcnow()+datetime.timedelta(hours=25) 
	isotime = timestamp.isoformat()
	commands= [
		'#!/usr/env bash',
		'aws ec2 request-spot-instances \\',
		'    --spot-price '+str(price)+' \\',
		'    --instance-count 1 \\',
		'    --type one-time \\',
		'    --valid-until '+str(isotime)+' \\',
		'    --launch-specification file://'+out+'.json \\'
		]
	ofh.write('\n'.join(commands)+'\n')
	ofh.close()
