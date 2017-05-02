from mailanalyzer.detector.abstract import AbstractDetector
import os
import glob
import re
import xml.etree.cElementTree as ET
from collections import defaultdict

class CustomHeaderDetector(AbstractDetector):
	
	def __init__(self):
		
		path = os.path.join(os.path.dirname(__file__),'customHeaders')
		files = glob.glob(path + '/*.xml')		

		self.customheaders = defaultdict(dict)
		
		# read from xml file and build list
		for xml in files:  
			tree = ET.parse(xml)
			chdata = tree.getroot()
			base = os.path.basename(xml)

			
			for service_tree in chdata.iter("Service"):
				service = service_tree.attrib['Name']
				
				for cheader_tree in service_tree.iter('CHeader'):
					customheader = cheader_tree.attrib['Name'].lower()	
					regexps = []
					
					for region_tree in cheader_tree.iter('Region'):
						region = region_tree.attrib['ID']
						
						# finds all domains in region 
						domains = []
						for domain_tree in region_tree.findall('Domain'):
							domain = domain_tree.attrib['Regex']
							domains.append(domain)
			
						# plain numbers are not allowed as capture group name, hence prefix with 'region'
						regexps.append('(?P<region{}>{})'.format(region, '|'.join(domains)))
				
					if len(regexps) > 0:
						self.customheaders[customheader][service] = re.compile('|'.join(regexps))
					else: 
						self.customheaders[customheader][service] = False
	
	def detect(self, headers, filename):
		providers = set()
		regions = set()
		notdetected = set()
		dkim_regex = re.compile(r'd=\s*([A-Za-z0-9\-\.]+)\s*;')
		
		for customheader in self.customheaders:
			if customheader in headers:
				detected = False
				for service in self.customheaders[customheader]:
					# We do not have a regex, thus existence of the field suffices
					if self.customheaders[customheader][service] == False:
						providers.add(service)
						regions.add('0')
						detected = True
					else:
						for match in self.customheaders[customheader][service].finditer(headers[customheader]):
							for region, value in match.groupdict().iteritems():
								if value != None:
									# remove prefix from capture group
									region = region.replace('region', '', 1)
									providers.add(service)
									regions.add(region)
									detected = True
									
				if not detected:
					if customheader in ['domainkey-signature', 'x-google-dkim-signature', 'dkim-signature']:
						domain = dkim_regex.search(headers[customheader])
						if domain is not None:
							notdetected.add(customheader + ' ' + domain.group(1))
						else:
							print 'ERROR dkim broken', filename
					else:
						notdetected.add(customheader)
		
		for header in headers:
			if header not in self.customheaders:
				if header not in ['received', 'received_ipv4', 'received_ipv6', 'to', 'cc', 'from', 'subject', 'date']:
					notdetected.add(header)
		
		return providers, regions, notdetected
				
