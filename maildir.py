#!/usr/bin/env python2

from mailanalyzer import statistics
from mailanalyzer import parsing
from collections import defaultdict
from mailanalyzer import detector
import datetime
import csv
import time
import os
import mailbox, email

# put a list of maildirs here
mailbox_dirs = [
	'',
]

# output path
output = 'output/{}_'.format(time.strftime('%Y%m%d_%H%M'))

# use this to blacklist a certain provider for a specific mailbox (because you are using this provider).
# You MUST use wildcards to match all files in a path

#detector.ignore_providers = {
#'*': 'Google'
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

# search for maildir subfolders
for dirname in mailbox_dirs:
	listofdirs = [dn for dn in os.walk(dirname).next()[1] if dn not in ['new', 'cur', 'tmp'] and dn[0] != '.']
	for curfold in listofdirs:
		filename = os.path.join(dirname, curfold)
        	if not (os.path.isdir(filename+"/new") and os.path.isdir(filename+"/cur") and os.path.isdir(filename+"/tmp")):
				continue
		maildir = mailbox.Maildir(filename, email.message_from_file)
		for msg in maildir:
			parsing.process_mail(msg, filename, stats)

stats.write_provider_data(output + 'provider_data.csv')
stats.write_hidden_provider_data(output + 'hidden_provider_data.csv')

