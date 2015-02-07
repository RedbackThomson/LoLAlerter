'''
	LoLAlerter: Every LoL partner's pal
	Copyright (C) 2015 Redback
	This file is part of LoLAlerter
'''

import json

class Settings(object):
	'''
	The Settings class is in charge of delivering the local configuration to
	each of the classes
	'''

	@classmethod
	def set_path(cls, path):
		'''
		Sets the path of the settings file
		
		:param path: The path to the settings file
		'''
		cls.path = path
		
	@classmethod
	def database(cls):
		'''
		Returns the array of database settings
		'''
		return cls.open_file()['database']
	
	@classmethod
	def redis(cls):
		'''
		Returns the array of redis settings
		'''
		return cls.open_file()['redis']
		
	@classmethod
	def open_file(cls):
		'''
		Opens the settings file and returns the json data
		'''
		return json.loads(open(cls.path, 'r').read())
	
Settings.set_path('../lolalerter.conf')