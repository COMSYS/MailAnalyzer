from mailanalyzer import detector
import mailbox
import email
import re
import datetime
import calendar
import pytz
import os
import gzip

# use workaround for SPAM dataset
spam_workaround = False

# set of all already seen message-ids
seen_message_ids = set()

# regex to match for ip addresses and hostnames in received lines
received_regex = re.compile(r'(?P<ipv4>(?<![0-9\.])(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?![0-9\.]))|[\s\(=](?P<hostname>[a-zA-Z\-0-9\.]+\.[a-zA-Z]+)|(?:IPv6\:)?(?P<ipv6>(?:(?:[0-9A-Fa-f]{1,4}:){7}(?:[0-9A-Fa-f]{1,4}|:))|(?:(?:[0-9A-Fa-f]{1,4}:){6}(?::[0-9A-Fa-f]{1,4}|(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(?:(?:[0-9A-Fa-f]{1,4}:){5}(?:(?:(?::[0-9A-Fa-f]{1,4}){1,2})|:(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(?:(?:[0-9A-Fa-f]{1,4}:){4}(?:(?:(?::[0-9A-Fa-f]{1,4}){1,3})|(?:(?::[0-9A-Fa-f]{1,4})?:(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(?:(?:[0-9A-Fa-f]{1,4}:){3}(?:(?:(?::[0-9A-Fa-f]{1,4}){1,4})|(?:(?::[0-9A-Fa-f]{1,4}){0,2}:(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(?:(?:[0-9A-Fa-f]{1,4}:){2}(?:(?:(?::[0-9A-Fa-f]{1,4}){1,5})|(?:(?::[0-9A-Fa-f]{1,4}){0,3}:(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(?:(?:[0-9A-Fa-f]{1,4}:){1}(?:(?:(?::[0-9A-Fa-f]{1,4}){1,6})|(?:(?::[0-9A-Fa-f]{1,4}){0,4}:(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(?::(?:(?:(?::[0-9A-Fa-f]{1,4}){1,7})|(?:(?::[0-9A-Fa-f]{1,4}){0,5}:(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))')
sender_regex = re.compile(r'[a-zA-Z0-9_\.+-]+@([a-zA-Z0-9-]+\.[a-zA-Z0-9-\.]+)')


# patch mailbox.mbox._generate_toc() for a stricter check of from lines
mailbox.mbox._comsyspatch_fromlinepattern = r"From \s*[^\s]+\s+\w\w\w\s+\w\w\w\s+\d?\d\s+" \
                       r"\d?\d:\d\d(:\d\d)?(\s+[^\s]+)?\s+\d\d\d\d\s*$"
mailbox.mbox._comsyspatch_regexp = None
def _generate_toc(self):
	if not self._comsyspatch_regexp:
		import re
		self._comsyspatch_regexp = re.compile(self._comsyspatch_fromlinepattern)
	"""Generate key-to-(start, stop) table of contents."""
	starts, stops = [], []
	last_was_empty = False
	self._file.seek(0)
	while True:
		line_pos = self._file.tell()
		line = self._file.readline()
		if self._comsyspatch_regexp.match(line):
			if len(stops) < len(starts):
				if last_was_empty:
					stops.append(line_pos - len(os.linesep))
				else:
					# The last line before the "From " line wasn't
					# blank, but we consider it a start of a
					# message anyway.
					stops.append(line_pos)
			starts.append(line_pos)
			last_was_empty = False
		elif not line:
			if last_was_empty:
				stops.append(line_pos - len(os.linesep))
			else:
				stops.append(line_pos)
			break
		elif line == os.linesep:
			last_was_empty = True
		else:
			last_was_empty = False
	self._toc = dict(enumerate(zip(starts, stops)))
	self._next_key = len(self._toc)
	self._file_length = self._file.tell()
mailbox.mbox._generate_toc = _generate_toc	


def parse_headers(mail):
	headers = dict()
	headers['received'] = []
	headers['received_ipv4'] = set()
	headers['received_ipv6'] = set()
	headers['received_hostname'] = set()
	headers['sendernames'] = set()

	for (key, value) in mail._headers:
		value = value.strip()
		
		if key.lower() == 'received':
			headers['received'].append(value)
		
			for match in received_regex.finditer(value):
				for group, matched in match.groupdict().iteritems():
					if matched != None:
						headers['received_' + group].add(matched)
		elif key.lower() in ['from', 'to', 'cc', 'bcc']: # bcc likely unnecessary, but better to be on the safe side
			senders = sender_regex.findall(value)
			for sender in senders:
				headers['sendernames'].add(sender.lower())
			headers[key.lower()] = value
		else:	
			headers[key.lower()] = value
		
	return headers		
	

'''
Processes a single email. 
Calls detector.detect and adds email statistics to stats instance.
'''
def process_mail(mail, filename, stats):
	global seen_message_ids

	headers = parse_headers(mail)

	if not 'message-id' in headers.keys():
		print 'ERROR missing message-id', filename
		return False
	
	if not 'date' in headers.keys():
		print 'ERROR missing date', filename
		return False
		
	if not len(headers['received']) > 0:
		print 'ERROR missing received header', filename
		return False
		
	# check if we have already seen a message with this message-id
	if headers['message-id'] in seen_message_ids:
		print 'ERROR duplicate message-id', headers['message-id'], filename
		return False
	seen_message_ids.add(headers['message-id'])
	
	# we use the top most (i.e., newest) received line to "timestamp" this e-mail
	r = headers['received'][0]
	date = r.split(';')[-1]

	# workaround for SPAM mails (use second top most recevied line for timestamping)
	if spam_workaround:
		if len(headers['received']) >= 2:
			r = headers['received'][1]
			date = r.split(';')[-1]
			
	# convert weird email datetime string to datetime object
	tt = email.utils.parsedate_tz(date)
	if tt is None or tt[9] is None:
		print 'ERROR time broken', filename
		return False
	
	timestamp = datetime.datetime.fromtimestamp(calendar.timegm(tt) - tt[9], pytz.UTC) 

	detected = detector.detect(headers, filename)
	stats.add(headers, timestamp, detected)
	return True

def process_mbox(filename, stats):
	msgs = mailbox.mbox(filename)
	for (j, mail) in enumerate(msgs):
		process_mail(mail, filename, stats)

def process_mbox_list(filenames, stats):
	for f in filenames:
		process_mbox(f, stats)

def process_mbox_dir(dir_name, stats):
	for path, subdirs, files in os.walk(dir_name):
		for name in files:
			if name.lower().endswith(('.mail', '.mbox', '.imap')):
				inbox = os.path.join(path, name)
				process_mbox(inbox, stats)
			else:
				print 'WARNING: strange file', name

def process_mailfile(filename, stats):
	with open(filename, 'r') as fp:
		mail = email.message_from_file(fp)
		process_mail(mail, filename, stats)

def process_mailfile_list(filenames, stats):
	for f in filenames:
		process_mailfile(f, stats)

def process_mailfile_dir(dir_name, stats):
	for path, subdirs, files in os.walk(dir_name):
		for name in files:
			if name.lower().endswith(('.mail', '.mbox', '.imap', '.tmp', '.eml')):
				inbox = os.path.join(path, name)
				process_mailfile(inbox, stats)
			else:
				print 'WARNING: strange file', name
				
def process_emlx(filename, stats):
	# source: https://gist.github.com/karlcow/5276813
	with open(filename, 'rb') as f:
		# extract the bytecount
		bytecount = int(f.readline().strip())
		# extract the message itself.
		mail = email.message_from_string(f.read(bytecount))
		process_mail(mail, filename, stats)

def process_emlx_list(filenames, stats):
	for f in filenames:
		process_emlx(f, stats)
