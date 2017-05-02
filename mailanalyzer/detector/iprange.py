from mailanalyzer.detector.abstract import AbstractDetector
import glob
import os
import re
import csv
import radix
import xml.etree.cElementTree as ET
import itertools

class IPRangeDetector(AbstractDetector):

	def __init__(self, files=None):
		
		if files == None:
			path = os.path.join(os.path.dirname(__file__),'ipRanges')
			files = glob.glob(path + '/*.xml')
		
		self.rtree = radix.Radix()	
		
		for xml in files:  
			try:
				tree = ET.parse(xml)
			except:
				print 'ERROR parsing XML file: ' + xml
			 
			ipdata = tree.getroot()
			base = os.path.basename(xml)
			name = ""
			
			for service_tree in ipdata.iter("Service"):
				name = service_tree.attrib.values()[0]
		
				regs = set()	
				for region_tree in service_tree.iter('Region'):
					reg = region_tree.attrib.values()[0]
					regs.add(reg)
				
					for iprange_tree in region_tree.findall('IpRange'):
						rng = iprange_tree.attrib.values()[0]	
					
						rnode = self.rtree.add(rng)
						rnode.data['Provider'] = name
						rnode.data['Region'] = reg
					
	
		# ignore private ip addresses (might boost performance)
		self.ignore = radix.Radix()
		self.ignore.add('10.0.0.0/8')
		self.ignore.add('127.0.0.0/8')
		self.ignore.add('172.16.0.0/12')
		self.ignore.add('192.168.0.0/16')
		
	def detect(self, headers, filename):
		providers = set()
		regions = set()
		notdetected = set()

		if not ('received_ipv4' in headers or 'received_ipv4' in headers):
			return providers, regions, notdetected

		for ip in itertools.chain(headers['received_ipv4'], headers['received_ipv6']):

			# we ignore private ip addresses
			if self.ignore.search_best(ip) is not None:
				continue
			
			found_node = self.rtree.search_best(ip)
			if found_node is not None:
				providers.add(found_node.data['Provider'])
				regions.add(found_node.data['Region'])
			
			else: 
				notdetected.add(ip) 
						
		return providers, regions, notdetected
