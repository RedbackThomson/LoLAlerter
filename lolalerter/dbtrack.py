'''
	LoLAlerter: Every LoL partner's pal
	Copyright (C) 2015 Redback
	This file is part of LoLAlerter
'''

import time

from actives import ActiveAlerter
from model import Alerter


class DBTracker(object):
	'''
	The DBTracker continuously reloads information from the database, so that
	any changes to the alerters modify the active alerters
	'''
	
	def __init__(self, lolalerter):
		'''
		Constructor
		
		:param lolalerter: The main LoLAlerter client
		'''
		self.alerters = []
		self.lolalerter = lolalerter
	
	def start(self):
		'''
		Begins tracking database changes
		'''
		self.alive = True
		
		while(self.alive):
			active_alerters = Alerter.select().where(Alerter.enabled)  # @UndefinedVariable
			
			active_set = set(x.id for x in active_alerters)
			current_set = set(x.model.id for x in self.alerters)
			
			old_alerters = current_set - active_set
			new_alerters = active_set - current_set
			
			self.disable_alerters([x for x in self.alerters 
								if x.model.id in old_alerters])
			self.activate_alerters([x for x in active_alerters 
									if x.id in new_alerters])
			
			time.sleep(5)
			
	def stop(self):
		'''
		Stops tracking database changes and stops all active alerters
		'''
		self.alive = False
		self.disable_alerters(self.alerters)
			
	def activate_alerters(self, alerters):
		'''
		Starts the new alerters
		
		:param alerters: The list of new alerters to activate
		'''
		for alerter in alerters:
			new_active = ActiveAlerter(self, alerter, self.lolalerter)
			new_active.start()
			
			self.alerters.append(new_active)
		
	def disable_alerters(self, alerters):
		'''
		Stops and removes a disabled alerter
		
		:param alerters: The list of current alerters to disable and remove
		'''
		for alerter in alerters:
			alerter.stop()
			self.alerters.remove(alerter)
		
	def global_message(self, twitch_username, message):
		'''
		Tries to send the message to a summoner attached to a given Twitch 
		username
		
		:param twitch_username: The Twitch username of the summoner
		:param message: The message to send to the user
		'''
		for alerter in self.alerters:
			summoner = alerter.get_summoner(twitch_username)
			if summoner != None:
				alerter.chat.new_message(summoner.summonerid, message)