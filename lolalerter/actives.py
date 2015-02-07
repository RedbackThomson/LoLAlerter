'''
	LoLAlerter: Every LoL partner's pal
	Copyright (C) 2015 Redback
	This file is part of LoLAlerter
'''

import re

from alerterredis import AlerterRedis
from logger import Logger
from model import *  # @UnusedWildImport
from riot.riotchat import RiotChat
from twitch.subtrack import SubTracker
from twitchalerts.DonateTracker import DonateTracker
import constants as Constants


class ActiveAlerter(object):
	'''
	An ActiveAlerter is a node of LoLAlerter tasked to track individuals
	under their control as set by the website.
	
	ActiveAlerters will house an active connection to the Riot chat servers and
	to maintain a local list of all active users within its control.
	'''

	def __init__(self, tracker, model, lolalerter):
		'''
		Constructor
		
		:param tracker: The tracker object assigned to this alerter
		:param model: The database model assosciated with the alerter
		:param lolalerter: The main LoLAlerter client
		'''
		self.tracker = tracker
		self.model = model
		self.lolalerter = lolalerter
		self.chat = RiotChat(self, model)
		self.users = []
		
	def start(self):
		'''
		Connects the alerter to chat and starts listening for users
		'''
		self.chat.start()
		
	def stop(self):
		''''
		Disconnects the alerter and all its active user threads
		'''
		self.chat.stop()
		for user in self.users:
			user.stop()
		self.users = []
		
	def restart(self):
		'''
		Disconnects and reconnects the bot
		'''
		self.stop()
		self.start()
		
	def user_online(self, summoner_id, retry=False):
		'''
		Handles a new user connecting to the chat
		
		:param summoner_id: The summoner ID of the new user
		:param retry: A boolean of whether the user has retried the login
		'''
		try:
			summoner = (ActiveSummoner 
				.select(ActiveSummoner, User)
				.join(User)
				.where(ActiveSummoner.summonerid == summoner_id)
				.get())
			Logger().get().info("User Online: {} ({} - {})".format(
				summoner.user.twitchusername, summoner.summonername,
				summoner.summonerid))
			
			if(retry):
				self.chat.new_message(summoner_id, 
					Constants.INACTIVE_NOW_ACTIVE)
		# Summoner is not an active user
		except ActiveSummoner.DoesNotExist:
			self.chat.new_message(summoner_id, Constants.INACTIVE_RESTART)
			Logger().get().info("Inactive User: {} ({} - {})".format(
				summoner.user.twitchusername, summoner.summonername,
				summoner.summonerid))
		
		try:
			self.setup_user(summoner)
			AlerterRedis().user_online(summoner)
		except Exception as err:
			import random
			reference = ('%05x' % random.randrange(16**5)).upper()
			
			message = str(Constants.ERROR_MESSAGE).format(ref=reference)
			self.chat.new_message(summoner_id, message)
			
			Logger().get().info('Exception reference: {}'.format(reference))
			Logger().get().exception(err)
			
	def user_offline(self, summoner_id):
		'''
		Handles a user disconnecting from the chat
		
		:param summoner_id: The summoner ID of the leaving user
		'''
		try:
			summoner = (ActiveSummoner 
				.select(ActiveSummoner, User)
				.join(User)
				.where(ActiveSummoner.summonerid == summoner_id)
				.get())
			Logger().get().info("User Offline: {} ({} - {})".format(
				summoner.user.twitchusername, summoner.summonername,
				summoner.summonerid))
		# Summoner is not an active user
		except ActiveSummoner.DoesNotExist:
			return
		
		for running in [x for x in self.users 
			if x.summoner.user.id == summoner.user.id]:
			running.stop()
			self.users.remove(running)
			
		AlerterRedis().user_offline(summoner.user)
			
	def setup_user(self, summoner):
		'''
		Sets up the new user and starts it
		
		:param summoner: The summoner of the new user
		'''
		self.user_notice_update(summoner)
		
		# Check the user isn't already running
		for running in [x for x in self.users 
			if x.summoner.user.id == summoner.user.id]:
			running.stop()
			self.users.remove(running)
		
		# Create the active user
		new_user = ActiveUser(self, summoner)
		new_user.start()
		
		# Add to the Twitch Chat
		self.lolalerter.chat.add_channel(new_user)
		
		self.users.append(new_user)
		
	def user_notice_update(self, summoner):
		'''
		Updates the user with any new notices
		
		:param summoner: The summoner to check for
		'''
		last = summoner.user.lastnotice.id
		
		for newer in Notice.select().where(Notice.id > last):
			self.chat.new_message(summoner.summonerid, 
				'[NOTICE] {}'.format(newer.message))
			
		try:
			# Modify latest notice in db
			user = summoner.user
			user.lastnotice = newer
			user.save()
		except UnboundLocalError:
			return
		
	def summoner_friend_requested(self, summoner_id, jid):
		'''
		Accepts or declines a user's friend request
		
		:param summoner_id: The summoner ID of the requesting user
		:param jid: The full JID of the requesting user
		'''
		acceptable = self.is_summoner(summoner_id)
		if acceptable:
			Logger().get().info('Friendship Accepted: {0}'.format(summoner_id))
			self.chat.sendPresence(pto=jid, ptype='subscribed')
			self.chat.sendPresence(pto=jid, ptype='subscribe')
			# Add to the table tracking friends
			AlerterFriend(alerter=self.model, summonerid=summoner_id).save()
			self.chat.new_message(summoner_id, Constants.ADDED_SUCCESS)
		else:
			Logger().get().info('Friendship Declined: {0}'.format(summoner_id))
			self.chat.sendPresence(pto=jid, ptype='unsubscribed')
			self.chat.sendPresence(pto=jid, ptype='unsubscribe')
			
	def summoner_friend_deleted(self, summoner_id):
		'''
		Responds to a user deleting the bot from their friends list
		
		:param summoner_id: The summoner ID of the deleting user
		'''
		Logger().get().info('Friendship Terminated: {0}'.format(summoner_id))
		self.user_offline(summoner_id)
		AlerterFriend.get(AlerterFriend.summonerid == summoner_id)\
			.delete_instance()
		
	def summoner_changed_presence(self, summoner_id, presence):
		'''
		Responds to the event of a summoner changing presence
		
		:param summoner_id: The summoner ID of the user that changed presence
		:param presence: The new presence of the summoner
		'''
		user = self.get_user(summoner_id)
		
		champion_regex = '<skinname>([\w ]+)<\/skinname>'
		lol_presence = presence['status']
		search = re.search(champion_regex, lol_presence)
		
		# Able to see a skin name; therefore in game
		if(search != None):
			groups = search.groups()
			if '<gameStatus>inGame</gameStatus>' in lol_presence \
			and len(groups) > 0:
				if user.champion != groups[0]:
					champion = groups[0]
					Logger().get().info('Summoner Started Game: {} ({}) [{}]'
						.format(user.summoner.summonername, 
							user.summoner.user.twitchusername, champion))
					AlerterRedis().summoner_ingame(summoner_id, champion)
					user.champion = champion
					
		# Unable to see a skin name, established out of game 
		else:
			AlerterRedis().summoner_outgame(summoner_id)
			user.champion = ''
		
	def new_subscriber(self, summoner, subscriber, resub):
		'''
		Triggers the events for a new subscriber
		
		:param summoner: The summoner in charge of the new subscriber
		:param subscriber: The new subscriber's username
		:param resub: A boolean of whether the user has already subscribed
		'''
		#TODO: Add database statistics
		try:
			messages = Message.get(Message.user == summoner.user)
			ingame = messages.ingame
			if resub:
				ingame = Constants.RESUB_FLAG + ingame
			
			if '%s' in ingame:
				self.chat.new_message(summoner.summonerid, ingame % subscriber)
			elif '{sub}' in ingame:
				self.chat.new_message(summoner.summonerid, 
					ingame.format(sub=subscriber))
			else:
				self.chat.new_message(summoner.summonerid, ingame)
		except Message.DoesNotExist:
			if resub:
				self.chat.new_message(summoner.summonerid, 
					str(Constants.RESUB_SUBSCRIBER).format(subscriber))
			else:
				self.chat.new_message(summoner.summonerid, 
					str(Constants.NEW_SUBSCRIBER).format(subscriber))
			
	def new_donation(self, summoner, donator, amount, message):
		'''
		Triggers the events for a new donator
		
		:param summoner: The summoner in charge of the new donation
		:param donator: The username of the donating user
		:param amount: The amount of the donation
		:param message: The message attached to the donation
		'''
		try:
			messages = Message.get(Message.user == summoner.user)
			donation_message = messages.newdonation
			
			if donation_message != None:
				self.chat.new_message(summoner.summonerid, 
					donation_message.format(
						amount=amount,
						user=donator,
						message=message
					));
			else:
				self.chat.new_message(summoner.summonerid, 
					str(Constants.NEW_DONATION).format(amount, donator))
		except Message.DoesNotExist:
			self.chat.new_message(summoner.summonerid, 
				str(Constants.NEW_DONATION).format(amount, donator))
		
	def is_summoner(self, summoner_id):
		'''
		Returns whether the provided summoner ID is a summoner for the
		alerter
		
		:param summoner_id: The summoner ID to check for the alerter
		'''
		return Summoner.select().where(Summoner.summonerid == summoner_id)\
			.exists()
		
	def get_summoner(self, twitch_username):
		'''
		Returns the online summoner attached to the given Twitch username
		
		:param twitch_username: The Twitch username to search for
		'''
		return next((x.summoner for x in self.users if 
			x.user.twitchusername == twitch_username), None)
		
	def get_user(self, summoner_id):
		'''
		Returns an ActiveUser by a specified summoner ID
		
		:param summoner_id: The summoner ID of the user to retrieve
		'''
		return next(
			(x for x in self.users if str(x.summoner.summonerid)  
				== str(summoner_id)), None)
		
	@property
	def online_users(self):
		'''
		Returns a list of all active users' usernames
		'''
		return [x.summoner.user.twitchusername for x in self.users]
			
	
class ActiveUser(object):
	'''
	An ActiveUser is a particular user identified as an active LoLAlerter user.
	
	The role of an ActiveUser is to house a subscriber tracker and donation 
	tracker.
	'''
	
	def __init__(self, alerter, summoner):
		'''
		Constructor
		
		:param alerter: The ActiveAlerter parent of the user
		:param summoner: The summoner associated with the user
		'''
		self.active_alerter = alerter
		self.summoner = summoner
		self.user = summoner.user
		self.sub_tracker = SubTracker(self)
		self.donation_tracker = DonateTracker(self)
		self.champion = ''
		
	def start(self):
		'''
		Starts the activeuser polling
		'''
		self.sub_tracker.start()
		self.donation_tracker.start()
		
	def stop(self):
		'''
		Stops the connections to activeuser
		'''
		self.sub_tracker.stop()
		self.donation_tracker.stop()
		self.champion = ''
		
	def new_subscriber(self, username, resub):
		'''
		Triggers the events for a new subscriber
		
		:param username: The username of the new subscriber
		:param resub: A boolean of whether the user is re-subscribing
		'''
		Logger().get().info("New Subscriber ({}) for {}({})".format(username, 
			self.user.twitchusername, self.summoner.summonerid))
		
		self.active_alerter.new_subscriber(self.summoner, username, resub)
		
	def new_donation(self, donator, amount, message):
		'''
		Triggers the events for a new donation
		
		:param donator: The user who donated the amount 
		:param amount: The amount of money that was donated
		:param message: The message attached to the donation
		'''
		Logger().get().info("New Donation ({} - {}) for {}({}) - {}".format(
			amount, donator, self.user.twitchusername, self.summoner.summonerid
			, message))
		
		self.active_alerter.new_donation(self.summoner, 
			donator, amount, message)
		
	def __eq__(self, other):
		if isinstance(other, ActiveUser):
			return self.summoner.id == other.summoner.id
		return NotImplemented