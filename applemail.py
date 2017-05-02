#!/usr/bin/env python

from mailanalyzer import statistics
from mailanalyzer import parsing
from collections import defaultdict
from mailanalyzer import detector
import datetime
import csv
import time
import os

# Put a list of Apple Mail directories here
mailbox_dirs = [
	'',
]

# output path
output = 'output/{}_'.format(time.strftime('%Y%m%d_%H%M'))

# use this to blacklist a certain provider for a specific mailbox (because you are using this provider).
# You MUST use wildcards to match all files in a path

#detector.ignore_providers = {
#'/path/*': 'Google'
#}

# Possible providers:
# 1and1                         AdobeMarketingCloud           Amazon
# AOL                           Apple                         AppRiver
# CenturyLink                   Cisco                         Comcast
# Epsilon                       ExperianMarketingServices     Fujitsu
# GoDaddy                       Google                        MAXMailProtection
# McAfee                        Microsoft                     Mimecast
# NTT Communications            Oracle                        OVH
# Proofpoint                    Rackspace                     Salesforce
# SoftLayer                     Strato                        Symantec
# TrendMicro                    Virtustream                   VMware
# Yahoo

# creates stats instance 
stats = statistics.DateStatistic(date_aggregation = '%Y-%m')

# search for emlx files
files = []
for mailbox_dir in mailbox_dirs:
	for root, dirnames, filenames in os.walk(mailbox_dir):
		for filename in filenames:
			if not filename.lower().startswith('._'):
				if filename.lower().endswith('.emlx'):
					files.append(os.path.join(root, filename))

parsing.process_emlx_list(files, stats)

stats.write_provider_data(output + 'provider_data.csv')
stats.write_hidden_provider_data(output + 'hidden_provider_data.csv')
