#!/usr/bin/env python

from mailanalyzer import statistics
from mailanalyzer import parsing
from collections import defaultdict
from mailanalyzer import detector
import datetime
import csv
import time
import os
import imaplib
import re
import email
import getpass

# IMAP configuration
M = imaplib.IMAP4_SSL('') # server
M.login('', getpass.getpass()) # username

# output path
output = 'output/{}_'.format(time.strftime('%Y%m%d_%H%M'))

# use this to blacklist a certain provider for this mailbox (because you are using this provider).

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

list_response_pattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')

rv, mailboxes = M.list()
if rv != 'OK':
	print 'ERROR: reading mailboxes'
	quit()

for mailbox in mailboxes:	
	flags, delimiter, mailbox_name = list_response_pattern.match(mailbox).groups()
	mailbox_name = mailbox_name.strip('"')

	rv, data = M.select(mailbox_name, readonly=True)
	if rv != 'OK':
	 	print 'ERROR: Cannot select mailbox', mailbox_name
	 	continue
	rv, data = M.uid('search', None, 'ALL')
	if rv != 'OK':
	 	print 'ERROR: Failed to search for messages', mailbox_name
	 	continue
	for num in data[0].split():
		rv, data2 = M.uid('fetch', num, '(RFC822)')
		if rv != 'OK':
			print "ERROR: getting message", num
		
		if data2 and len(data2) > 1:
			email_message = email.message_from_string(data2[0][1])
			parsing.process_mail(email_message, '{}/{}'.format(mailbox_name, num), stats)

stats.write_provider_data(output + 'provider_data.csv')
stats.write_hidden_provider_data(output + 'hidden_provider_data.csv')
