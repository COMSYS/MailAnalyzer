import abc

class AbstractDetector(object):
	__metaclass__ = abc.ABCMeta
		
 	@abc.abstractmethod
	def detect(self, headers, filename=''):
		"""This function implements one detector. It receivces the headers of
		   one email (as a dict) and return the set of detected cloud providers,
		   the set of detected regions, and a set of not detected values"""
		return
