'''
	LoLAlerter: Every LoL partner's pal
	Copyright (C) 2015 Redback
	This file is part of LoLAlerter
'''

from datetime import datetime
from queue import Queue
from urllib.request import urlopen
import json
import threading
import time
import urllib.error

from alerterredis import AlerterRedis
from logger import Logger
from model import Subscriber as SubModel
from model import User, ActiveUser
import constants as Constants


class SubTracker(object):
	'''
	The SubTracker is responsible for continuously checking for new users 
	subscribed to a given Twitch partner
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
		Begins tracking subscriber changes
		'''
		self.alive = True
		
		# Create a new thread for each sub tracker
		self.run_thread = threading.Thread(target=self.run_method)
		self.run_thread.start()
			
	def stop(self):
		'''
		Stops tracking subscriber changes
		'''
		self.alive = False
		
	def run_method(self):
		'''
		The method on which the thread will run
		'''
		first = True
		
		while(self.alive):
			# Get the latest few subscribers
			redis = AlerterRedis()
			latest = Subscriber.fetch(5, self)
			
			for new in latest:
				username = new['user']['display_name']
				twitch_id = new['user']['_id']
				
				# Store the overnight subscribers in the redis server
				if first:
					redis.new_subscriber(self.user, username)
					continue
				
				if (not redis.has_subscriber(self.user, username)):
					redis.new_subscriber(self.user, username)
					
					self.active_user.new_subscriber(username, 
						SubTracker.db_exists(self.user, twitch_id))
					
					# Update database after notification, otherwise it will
					# invalidate the resub ability
					new_sub = SubTracker.create_sub_model(self.user, 
						new['user'])
					new_sub.active = 1
					new_sub.save()
			
			first = False
			
			time.sleep(5)
			
	def refresh_token(self):
		'''
		Refreshes the token in the un-persistent cache
		'''
		self.user = User.get(User.id == self.user.id)
			
	@staticmethod
	def db_exists(user, twitch_id):
		'''
		Returns whether the subscriber already exists in the database for this
		particular user
		
		:param user: The user who may own the particular subscriber
		:param twitch_id: The Twitch ID of the user
		'''
		return SubModel.select().where(SubModel.user == user,  # @UndefinedVariable
			SubModel.twitchid == twitch_id).exists()  # @UndefinedVariable
	
	
	@staticmethod
	def create_sub_model(user, subscriber):
		'''
		Returns a subscriber model object containing nformation	given by the 
		Twitch API JSON data or the DB if it exists
		
		:param user: The user associated with the new subscriber
		:param subscriber: The Twitch API JSON data for the subscriber
		'''
		if SubTracker.db_exists(user, subscriber['_id']):
			return SubModel.get(SubModel.user == user,  # @UndefinedVariable
				SubModel.twitchid == subscriber['_id'])
		
		new_sub = SubModel()
		new_sub.user = user
		new_sub.twitchid = subscriber['_id']
		new_sub.username = subscriber['name']
		new_sub.displayname = subscriber['display_name']
		new_sub.adddate = subscriber['created_at']\
			.replace('Z', '').replace('T', ' ')
		
		return new_sub
		
		
class UnsubTracker(object):
	'''
	The UnsubTracker makes sure that all subscribers are accounted for in the 
	database, and also makes sure that any subscribers who have since chosen
	to unsubscribe will be marked as such
	'''
		
	def start(self):
		'''
		Begins tracking subscriber changes
		'''
		self.alive = True
		
		# Create a new thread for this background process
		self.run_thread = threading.Thread(target=self.run_method)
		self.run_thread.start()
			
	def stop(self):
		'''
		Stops tracking subscriber changes
		'''
		self.alive = False
		
	def run_method(self):
		'''
		The method on which the thread will run
		'''
		first = True
		
		# time.sleep(10)
		
		while(self.alive):
			Logger().get().info('Unsub Tracker Starting')
			# New subs and un subs
			self.stats = (0, 0)
				
			q = Queue()
			workers = []
			
			def worker():
				while True:
					self.update_subs(q.get())
					q.task_done()
				
			# Use 10 worker threads
			for i in range(10):
				t = threading.Thread(target=worker)
				t.setDaemon(True)
				workers.append(t)
				t.start()
				
			for user in ActiveUser.select():  # @UndefinedVariable
				q.put(user)
				
			q.join()
			
			Logger().get().info('Unsub Tracker Finished ({} new, {} unsub)'\
				.format(self.stats[0], self.stats[1]))
			
			time.sleep(30 * 60)
				
	def update_subs(self, user):
		'''
		Updates the subscribers for a particular user
		
		:param user: The ActiveUser model object to update for
		'''
		stats = (0, 0)
		twitch_current = Subscriber.fetch_all(user.twitchusername, 
			user.twitchtoken)
		if twitch_current == None: return
		twitch_ids = [x['user']['_id'] for x in twitch_current]
		
		current_models = SubModel.select(SubModel.twitchid)\
			.where(SubModel.user == user, SubModel.active)
		db_current = [x.twitchid for x in current_models]
		
		new_subs = [x for x in twitch_current if x['user']['_id'] not in 
			db_current]	
		un_subs = [x for x in db_current if x not in twitch_ids]
		
		for sub in new_subs:
			new_sub = SubTracker.create_sub_model(user, sub['user'])
			new_sub.active = 1
			new_sub.save()			
		
		if un_subs:
			SubModel.update(active=False, unsubdate=datetime.now())\
				.where(SubModel.twitchid << un_subs, SubModel.user == user).execute()
				
		stats = (len(new_subs), len(un_subs))
		
		self.stats = tuple(map(sum,zip(self.stats, stats)))
		
class Subscriber(object):
	'''
	A subscriber is a representation of a user subscribed to a particular
	Twitch channel
	'''

	@staticmethod
	def fetch(count, tracker):
		'''
		Fetches a list of the latest subscribers
		
		:param count: The amount of subscribers to fetch
		:param tracker: The tracker in charge of the users
		'''
		url = str(Constants.SUBSCRIBER_URI).format(
			username=tracker.user.twitchusername, limit=count, offset=0, 
			token=tracker.user.twitchtoken, timestamp=time.time())
		
		try:			
			response = urlopen(url).read()
			return Subscriber.parse_subscribers(response.decode('utf8'))
			
		except urllib.error.HTTPError as e:
			if(e.code == 401):
				Logger().get().error('Token expired ({}) - {}'.format(
					tracker.user.twitchusername, tracker.user.twitchtoken))
				tracker.refresh_token()
			elif(e.code != 422):
				Logger().get().error(e)
			return []
		
		except urllib.error.URLError as e:
			tracker.refresh_token()
			Logger().get().exception(e)
			return []
		
	@staticmethod
	def fetch_all(username, token):
		'''
		Fetches a large list of all subscribers
		
		:param username: The username of the twitch user
		:param token: The oauth token with the subscriber scope
		'''
		final = False
		offset = 0
		subs = []
		while(not final):
			url = str(Constants.SUBSCRIBER_URI).format(
				username=username, limit=100, 
				offset=offset, token=token, timestamp=time.time())
		
			try:
				response = urlopen(url).read()
				new_subs = json.loads(response.decode('utf8'))
				if 'error' in new_subs:
					final = True
				if not new_subs['subscriptions']:
					final = True
				else:
					subs.extend(new_subs['subscriptions'])
					offset += 100
				
			except Exception as err:
				final = True
				return None
		return subs
	
	@staticmethod
	def parse_subscribers(response):
		'''
		Parses the Twitch API JSON data into a list of subscriber objects
		
		:param response: The JSON data from the Twitch API
		'''
		subs = json.loads(response)
		# Reverse the list to show oldest donations first
		return subs['subscriptions'][::-1]