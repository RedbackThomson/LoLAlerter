'''
	LoLAlerter: Every LoL partner's pal
	Copyright (C) 2015 Redback
	This file is part of LoLAlerter
'''

import logging.config

import os

class Logger(object):
	'''
	The logger takes care of all of the logging setup. It can be easily
	imported instead of instantiating a new logger in every file
	'''

	def __init__(self):
		'''
		Constructor
		'''
		logging.config.fileConfig(os.path.join(os.path.dirname(__file__), 
			"../logging.conf"))
		self.log = logging.getLogger()
		
	def get(self):
		'''
		Gets the active logger
		'''
		return self.log