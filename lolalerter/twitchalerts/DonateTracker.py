'''
	LoLAlerter: Every LoL partner's pal
	Copyright (C) 2015 Redback
	This file is part of LoLAlerter
'''

import time
import threading
import json
import urllib.error
from logger import Logger
from alerterredis import AlerterRedis
import constants as Constants

class DonateTracker(object):
	'''
	The DonateTracker is in charge of detecting new donations through the
	TwitchAlerts API. It will send the donations through to the users' chat
	when a new donation arrives. 
	'''

	def __init__(self, active_user):
		'''
		Constructor
		:param user: The associated database user model associated
		'''
		self.active_user = active_user
		self.user = active_user.summoner.user
		
	def start(self):
		'''
		Begins tracking donation changes
		'''
		self.alive = True
		
		# Create a new thread for each sub tracker
		self.run_thread = threading.Thread(target=self.run_method)
		self.run_thread.start()
			
	def stop(self):
		'''
		Stops tracking donation changes
		'''
		self.alive = False
		
	def run_method(self):
		'''
		The method on which the thread will run
		'''
		first = True
		
		while(self.alive):
			# Get the latest few donations
			redis = AlerterRedis()
			latest = Donation.fetch(5, self.user.twitchalertskey)
			
			for new in latest:
				donate_id = new['id']
				
				# Store the overnight donations in the redis server
				if first:
					redis.new_donation(self.user, donate_id)
					continue
				
				if (not redis.has_donation(self.user, donate_id)):
					redis.new_donation(self.user, donate_id)
					#TODO: Put in database insert
					if(self.user.minimumdonation != None and 
						float(new['amount']) < self.user.minimumdonation):
						continue
					 
					self.active_user.new_donation(new['donator']['name'],
						new['amount'], new['message'])
			
			first = False
			
			# Minimum cache time by TwitchAlerts
			time.sleep(20)
		
class Donation(object):
	'''
	A donation is a representation of a donation towards a particular
	Twitch channel
	'''

	@staticmethod
	def fetch(count, key):
		'''
		Fetches a list of the latest donations
		
		:param count: The amount of donations to fetch
		:param key: The auth key for the TwitchAlerts API
		'''
		url = str(Constants.TWITCHALERTS_URI).format(token=key)
		
		try:			
			opener = urllib.request.build_opener()
			opener.addheaders = [('User-agent', 'LoLAlerter')]
			open = opener.open(url)
			response = open.read()
			return Donation.parse_donations(response.decode('utf8'))[:count]
			
		except urllib.error.HTTPError as e:
			if(e.code != 404):
				Logger().get().exception(e)
			return []
		
		except urllib.error.URLError as e:
			Logger().get().exception(e)
			return []
		
	@staticmethod
	def parse_donations(response):
		'''
		Parses the TwitchAlerts API JSON into donation objects
		
		:param response: The JSON data from the TwitchAlerts API
		'''
		subs = json.loads(response)
		return subs['donations']