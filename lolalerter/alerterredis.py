'''
	LoLAlerter: Every LoL partner's pal
	Copyright (C) 2015 Redback
	This file is part of LoLAlerter
'''

import redis


class AlerterRedis(object):
	'''
	The redis class handles the custom connection to the redis database for
	LoLAlerter.
	'''

	@classmethod
	def configure(cls, setting_array):
		'''
		Configures the redis Login
		'''
		cls.host = setting_array['host']
		cls.password = setting_array['password']
		cls.port = setting_array['port']
		cls.db = setting_array['db']

	def __init__(self):
		'''
		Constructor
		
		:param host: The host of the redis server
		:param password: The password for the redis server
		:param port: The port of the redis server
		:param db: The database for this particular application
		'''
		self.r = redis.StrictRedis(host=AlerterRedis.host,  # @UndefinedVariable
			password=AlerterRedis.password, port=AlerterRedis.port, 
			db=AlerterRedis.db)

	def new_subscriber(self, user, subscriber):
		'''
		Adds a new subscriber to a user's set
		
		:param user: The user associated with the new subscriber
		:param subscriber: The username of the new subscriber
		'''
		self.r.sadd('subscribers:'+user.apikey, subscriber)

	def has_subscriber(self, user, subscriber):
		'''
		Returns whether the user already has that subscriber
		
		:param user: The user associated with the subscriber
		:param subscriber: The username of the subscriber
		'''
		return self.r.sismember('subscribers:'+user.apikey, subscriber)

	def new_donation(self, user, donation_id):
		'''
		Adds a new donation to a user's set
		
		:param user: The user associated with the new donation
		:param donation_id: The twitch alerts ID for the donation
		'''
		self.r.sadd('donations:'+user.apikey, donation_id)

	def has_donation(self, user, donation_id):
		'''
		Returns whether the user already has that donation
		
		:param user: The user associated with the donation
		:param donation_id: The twitch alerts ID for the donation
		'''
		return self.r.sismember('donations:'+user.apikey, donation_id)

	def user_online(self, summoner):
		'''
		Changes the user's online summoner ID
		
		:param summoner: The summoner that has come online
		'''
		self.r.hset('online', summoner.user.apikey, summoner.summonerid)

	def user_offline(self, user):
		'''
		Removes the user's online summoner ID
		
		:param user: The user whose summoner to remove
		'''
		self.r.hdel('online', user.apikey)

	def summoner_ingame(self, summoner_id, champion):
		'''
		Change the champion of a particular summoner
		
		:param summoner_id: The summoner ID playing the champion
		:param champion: The name of the champion to change to
		'''
		self.r.hset('champion', summoner_id, champion)

	def summoner_outgame(self, summoner_id):
		'''
		Remove the champion data for a particular summoner
		
		:param summoner_id: The summoner ID of the champion data to delete
		'''
		self.r.hdel('champion', summoner_id)

	def twitch_command(self, user, username, command):
		'''
		Creates a new twitch command log line
		
		:param user: The user owning the channel of the command
		:param username: The username of the command caller
		:param command: The name of the called command
		'''
		self.r.lpush('twitch:'+user.APIKey, username+':!'+command)

	def clear(self):
		'''
		Removes current online data
		'''
		self.r.delete('online')
		self.r.delete('champion')	