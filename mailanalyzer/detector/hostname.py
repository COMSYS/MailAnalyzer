from mailanalyzer.detector.abstract import AbstractDetector
import os
import glob
import re
import csv
import xml.etree.cElementTree as ET

class HostNameDetector(AbstractDetector):
	
	def __init__(self):
		path = os.path.join(os.path.dirname(__file__),'domainRegex')
		files = glob.glob(path + '/*.xml')
		
		self.hostnames = dict()
	
		for xml in files:  
			tree = ET.parse(xml)
			hndata = tree.getroot()
			base = os.path.basename(xml)
			
			for service_tree in hndata.iter("Service"):
				service = service_tree.attrib.values()[0]
				regexps = []
			
				for region_tree in service_tree.iter('Region'):
					region = region_tree.attrib.values()[0]
			
					# finds all hostnames in region 
					hostnames = []
					for regex_tree in region_tree.findall('Regex'):
						hst = regex_tree.attrib.values()[0]
						hostnames.append(hst)
			
					# plain numbers are not allowed as capture group name, hence prefix with 'region'
					regexps.append('(?P<region{}>{})'.format(region, '|'.join(hostnames)))

				self.hostnames[service] = re.compile('|'.join(regexps))
		
	def detect(self, headers, filename):
		providers = set()
		regions = set()
		notdetected = set()
		
		if not 'received_hostname' in headers:
			return providers, regions, notdetected
		
		for line in headers['received_hostname']:
			detected = False
			for service in self.hostnames:
				match = self.hostnames[service].match(line)
				if match != None:
					for region, value in match.groupdict().iteritems():
						if value != None:
							# remove prefix from capture group
							region = region.replace('region', '', 1)
							providers.add(service)
							regions.add(region)
							detected = True
							
			if not detected:
				notdetected.add(line)
							
		return providers, regions, notdetected
