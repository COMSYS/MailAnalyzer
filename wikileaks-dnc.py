#!/usr/bin/env python

from mailanalyzer import statistics
from mailanalyzer import parsing
from collections import defaultdict
from mailanalyzer import detector
import datetime
import csv
import time

# path to directory with Wikileaks DNC archive
dir_name = ''
# output path
output = 'output/wikileaks-dnc/{}_'.format(time.strftime('%Y%m%d_%H%M'))

# creates stats instance 
datestats = statistics.DateStatistic(date_aggregation = '%Y-%m')

detector.ignore_providers = {
'*': 'AppRiver'
}

parsing.process_mailfile_dir(dir_name, datestats)

datestats.write_provider_data(output + 'provider_data.csv')
datestats.write_hidden_provider_data(output + 'hidden_provider_data.csv')
