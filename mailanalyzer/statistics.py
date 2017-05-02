import abc
from collections import defaultdict
from mailanalyzer import detector
import csv

class AbstractStatistic(object):
	__metaclass__ = abc.ABCMeta
	
 	@abc.abstractmethod
	def add(self, headers, timestamp, detected):
		"""This function takes the header, timestamp, and a dictionary of
		   detected cloud services and adds them to the statistic"""
		return
	
 	@abc.abstractmethod
	def get(self):
		"""This function returns the statistics object"""
		return

class MultiplexStatistic(AbstractStatistic):

	def __init__(self, stats):
		self.stats = stats
	
	def add(self, headers, timestamp, detected):
		for stat in self.stats:
			# detected might be altered by statistic modules, so better create a copy
			stat.add(headers, timestamp, dict(detected))
	
	def get(self):
		return self.stats

class SimpleStatistic(AbstractStatistic):
	
	def __init__(self):
		self.mails_per_provider = defaultdict(int)
		self.mails_per_region = defaultdict(int)
		self.mails_total = 0
		return
		
	def add(self, headers, timestamp, detected):
		self.mails_total += 1
		
		# keep track of providers and regions to avoid counting them twice if 
		# they were detected by different detectors
		providers = set()
		regions = set()
		
		for detector in detected:
					
			for provider in detected[detector]['providers']:
				if provider not in providers:
					providers.add(provider)
					self.mails_per_provider[provider] += 1
				
			for region in detected[detector]['regions']:
				if region not in regions:
					regions.add(region)
					self.mails_per_region[region] += 1
					
	def get(self):
		return self.mails_per_provider, self.mails_per_region, self.mails_total
	
	def get_dates(self):
		return self.dates	
		
	def get_regions(self):
		return self.regions
		
class DateStatistic(AbstractStatistic):
	
	def __init__(self, date_aggregation = '%Y-%m'):
		self.mails_per_provider = defaultdict(lambda : defaultdict(int))
		self.hidden_mails_per_provider = defaultdict(lambda : defaultdict(int))
		self.mails_per_region = defaultdict(lambda : defaultdict(int))
		self.mails_total = defaultdict(int)
		self.mails_detected = defaultdict(int)
		self.hidden_full = defaultdict(int)
		self.hidden_partial = defaultdict(int)
		self.date_aggregation = date_aggregation
		return
		
	def add(self, headers, timestamp, detected):
		d = timestamp.strftime(self.date_aggregation)
		self.mails_total[d] += 1
		
		# sender information is only used to detect hidden cloud usage
		sender_information = detected.pop('SenderDetector')
				
		providers = set.union(*[i['providers'] for i in detected.values()])
		regions = set.union(*[i['regions'] for i in detected.values()])
		
		if len(providers) > 0:
			self.mails_detected[d] += 1
		
		count_hidden = 0
		for provider in providers:
			self.mails_per_provider[d][provider] += 1
			if provider not in sender_information['providers']:
				self.hidden_mails_per_provider[d][provider] += 1
				count_hidden += 1
		
		# there is hidden cloud usage
		if count_hidden > 0:
			# atleast one cloud service is hidden
			self.hidden_partial[d] += 1
			if count_hidden == len(providers):
				# all cloud services are hidden
				self.hidden_full[d] += 1
		
		for region in regions:
			self.mails_per_region[d][region] += 1
					
	def get(self):
		return self.mails_per_provider, self.mails_per_region, self.mails_total
	
	def get_dates(self):
		return self.mails_total.keys()
		
	def get_providers(self):
		return list({j for i in self.mails_per_provider.values() for j in i})
		
	def get_provider_data(self):
		return self.mails_per_provider

	def get_region_data(self):
		return self.mails_per_region

	def get_regions(self):
		return list({j for i in self.mails_per_region.values() for j in i})

	def write_stats(self, filename):
		with open(filename, 'a') as f:
			total_per_provider = defaultdict(int)
			for entry in self.mails_per_provider.values():
				for k in entry:
					total_per_provider[k] += entry[k]
			f.write('Providers: {}\n'.format(dict(total_per_provider)))
			total_per_region = defaultdict(int)
			for entry in self.mails_per_region.values():
				for k in entry:
					total_per_region[k] += entry[k]
			f.write('Regions: {}\n'.format(dict(total_per_region)))
			f.write('# Mails: {}\n'.format(sum(self.mails_total.values())))

	def write_provider_data(self, filename):
		with open(filename, 'w') as f:
			dates = sorted(self.get_dates())
			providers = sorted(self.get_providers())
			header = ['Date', 'Total Mails', 'Total Detected', 'Hidden Partial', 'Hidden Full'] + providers
			csvwriter = csv.DictWriter(f, fieldnames = header, delimiter =';')
			csvwriter.writeheader()
			for date in dates:
				csvwriter.writerow(dict(
					{'Date':           date, 
					 'Total Mails':    self.mails_total[date], 
					 'Total Detected': self.mails_detected[date],
					 'Hidden Partial': self.hidden_partial[date],
					 'Hidden Full':    self.hidden_full[date],
					},
					**self.mails_per_provider[date]
				))

	def write_hidden_provider_data(self, filename):
		with open(filename, 'w') as f:
			dates = sorted(self.get_dates())
			providers = sorted(self.get_providers()) # it should be safe to use this function here
			header = ['Date', 'Total Mails', 'Total Detected', 'Hidden Partial', 'Hidden Full'] + providers
			csvwriter = csv.DictWriter(f, fieldnames = header, delimiter =';')
			csvwriter.writeheader()
			for date in dates:
				csvwriter.writerow(dict(
					{'Date':           date, 
					 'Total Mails':    self.mails_total[date], 
					 'Total Detected': self.mails_detected[date],
					 'Hidden Partial': self.hidden_partial[date],
					 'Hidden Full':    self.hidden_full[date],
					},
					**self.hidden_mails_per_provider[date]
				))

	def write_region_data(self, filename):
		with open(filename, 'w') as f:
			dates = sorted(self.get_dates())
			regions = sorted(self.get_regions())
			header = ['Date', 'Total Mails', 'Total Detected', 'Hidden Partial', 'Hidden Full'] + regions
			csvwriter = csv.DictWriter(f, fieldnames = header, delimiter =';')
			csvwriter.writeheader()
			for date in dates:
				csvwriter.writerow(dict(
					{'Date':           date, 
					 'Total Mails':    self.mails_total[date], 
					 'Total Detected': self.mails_detected[date],
					 'Hidden Partial': self.hidden_partial[date],
					 'Hidden Full':    self.hidden_full[date],					 
					},
					**self.mails_per_region[date]
				))

class DebugStatistic(AbstractStatistic):
	
	def __init__(self, filename):
		self.f = open(filename, 'w')
		header = ['Date', 'Message-ID', 'From', 'To', 'CC', 'Providers', 'Regions']
		for t in ['Providers', 'Regions']:
			for d in detector.detectors:
				header.append('{} {}'.format(t,  d.__class__.__name__))
		self.csvwriter = csv.DictWriter(self.f, fieldnames = header, delimiter =';')
		self.csvwriter.writeheader()
	
	def add(self, headers, timestamp, detected):
		# sender information is only used to detect hidden cloud usage
		reallydetected = dict(detected)
		sender_information = reallydetected.pop('SenderDetector')
				
		providers = set.union(*[i['providers'] for i in reallydetected.values()])
		regions = set.union(*[i['regions'] for i in reallydetected.values()])
		
		# default region is uninteresting
		regions.discard('0')
		
		if len(providers) == 0 and len(regions) == 0:
			return
		
		row = {
			'Date':       timestamp,
			'Message-ID': headers['message-id'],
			'Providers': ', '.join(providers),
			'Regions': ', '.join(regions),
		}
		for field in ['From', 'To', 'CC']:
			if field.lower() in headers:
				row[field] = headers[field.lower()].replace(';', ',').replace('\n', ' ')
		
		for detector in detected:
			row['Providers {}'.format(detector)] = ', '.join(detected[detector]['providers'])
			detected[detector]['regions'].discard('0')
			row['Regions {}'.format(detector)] = ', '.join(detected[detector]['regions'])

		self.csvwriter.writerow(row)
		
		return

	
	def get(self):
		return
		
	def __del__(self):
		self.f.close()
		
class UndetectedStatistic(AbstractStatistic):

	def __init__(self):
		self.undetected = defaultdict(lambda : defaultdict(int))
		
	def add(self, headers, timestamp, detected):
		for detector in detected:
			for elem in detected[detector]['notdetected']:
				self.undetected[detector][elem] += 1
		return
		
	def write(self, key, filename):
		with open(filename, 'w') as f:
			csvwriter = csv.DictWriter(f, fieldnames = ['Element', 'Count'], delimiter =';')
			csvwriter.writeheader()
			for key, value in sorted(self.undetected[key].iteritems(), key=lambda (k,v): (v,k),reverse=True):
				csvwriter.writerow({'Element': key, 'Count': value})
	
	def get(self):
		return
