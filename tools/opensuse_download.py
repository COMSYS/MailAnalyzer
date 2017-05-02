#!/usr/bin/env python

import urllib2
from urllib import urlretrieve
import re
import os
import time
import sys

base_url = 'https://lists.opensuse.org/'
output_folder = 'output/'
retry_timeout=1
retry_count=2

archive_overview_regex = re.compile(r'<th style="text-align:left; vertical-align:top;"><a href="([a-zA-Z0-9\-]+)">')
mbox_overview_regex = re.compile(r'.*<td class="list"><a href="([a-zA-Z0-9\-]+\.mbox\.gz)">')

def getPage(link):
    request = urllib2.Request(link)
    try:
        response = urllib2.urlopen(request)
    except IOError:
        return False
    else:
        return response.read()
        
def downloadFile(link, filename, retry=retry_count):
	dirname = os.path.dirname(filename)
	if not os.path.exists(dirname):
		os.makedirs(dirname)
	print ' Downloading {}...'.format(filename)
	try:
		response = urllib2.urlopen(link)
		CHUNK = 16 * 1024
		with open(filename, 'wb') as f:
			while True:
				chunk = response.read(CHUNK)
				if not chunk: 
					break
				f.write(chunk)
	except Exception,e:
		print ' * Failed to download: urlopen returned {}.'.format(e)
		if retry > 0:
			time.sleep(retry_timeout)
			downloadFile(link, filename, retry - 1)
		else:
			print ' * Failed to download: File unavailable, exceeded retry count. Skipping...'
			

html = getPage(base_url)

if not html:
	print 'Failed to download archive overview'
	quit()
	
archives = archive_overview_regex.findall(html)

for archive in archives:
	archive_html = getPage(base_url + archive)
	if not archive_html:
		print 'Failed to download mbox overview ' + archive
	
	mboxes = mbox_overview_regex.findall(archive_html)

	for mbox in mboxes:
		# download this mbox
		downloadFile(base_url + archive + '/' + mbox, output_folder + archive + '/' + mbox)
		sys.stdout.flush()

