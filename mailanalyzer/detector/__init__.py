import abc
import sys
import inspect
import pkgutil
from time import time
import fnmatch

# load AbstractDetector class
from abstract import AbstractDetector

# deactivate detector modules here
#module_blacklist = ['customheader']
module_blacklist = []

# possibility to ignore certain providers
ignore_providers = dict()

# Load all detector modules that are not listed in blacklist
for loader, module_name, is_pkg in  pkgutil.walk_packages(__path__):
	full_module_name = '%s%s' % (__path__, module_name)
	if full_module_name not in sys.modules:
		if module_name not in module_blacklist + ['abstract']:
			module = loader.find_module(module_name).load_module(full_module_name)
			print 'Loaded detector module "%s"' % module_name

# Creates an instance of each loaded detector class
detectors = []
for cls in AbstractDetector.__subclasses__():
	detectors.append(cls())

# This function takes the headers of one email, inputs them into each detector
# and returns the combined result
def detect(headers, filename):
	global detectors
	providers = set()
	regions = set()
	
	detected = {}

	for detector in detectors:
		
		detected[detector.__class__.__name__] = {} 
		p, r, n = detector.detect(headers, filename)

		# Ignore certain providers
		for ignore in ignore_providers:
			if fnmatch.fnmatch(filename, ignore):
				p.discard(ignore_providers[ignore])

		detected[detector.__class__.__name__]['providers'] = p
		detected[detector.__class__.__name__]['regions'] = r
		detected[detector.__class__.__name__]['notdetected'] = n
		
	return detected
