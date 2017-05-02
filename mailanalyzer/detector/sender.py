from mailanalyzer.detector.abstract import AbstractDetector
import os
import glob
import re
import xml.etree.cElementTree as ET

class SenderDetector(AbstractDetector):
	
	def __init__(self):
		# to be extra careful, we also add all domainRegex as valid sendernames
		path = os.path.join(os.path.dirname(__file__),'domainRegex')
		files = glob.glob(path + '/*.xml')
		
		path = os.path.join(os.path.dirname(__file__),'senderRegex')
		files = files + glob.glob(path + '/*.xml')
		
		self.senders = dict()
	
		for xml in files:  
			tree = ET.parse(xml)
			senderdata = tree.getroot()
			base = os.path.basename(xml)
			
			for service_tree in senderdata.iter("Service"):
				service = service_tree.attrib['Name']
				regexps = []
			
				for region_tree in service_tree.iter('Region'):
					region = region_tree.attrib['ID']
			
					# finds all sendernames in region 
					sendernames = []
					for regex_tree in region_tree.findall('Regex'):
						snd = regex_tree.attrib['Regex']
						sendernames.append(snd)
			
					# plain numbers are not allowed as capture group name, hence prefix with 'region'
					regexps.append('(?P<region{}>{})'.format(region, '|'.join(sendernames)))

				self.senders[service] = re.compile('|'.join(regexps))
		
	def detect(self, headers, filename):
		providers = set()
		regions = set()
		notdetected = set()
		
		for sendername in headers['sendernames']:
			detected = False
			for service in self.senders:
				for match in self.senders[service].finditer(sendername):
					for region, value in match.groupdict().iteritems():
						if value != None:
							# remove prefix from capture group
							region = region.replace('region', '', 1)
							providers.add(service)
							regions.add(region)
							detected = True
							
			if not detected:
				notdetected.add(sendername)
							
		return providers, regions, notdetected
