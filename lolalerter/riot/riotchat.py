'''
	LoLAlerter: Every LoL partner's pal
	Copyright (C) 2015 Redback
	This file is part of LoLAlerter
'''

import ssl

from sleekxmpp.clientxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout

from logger import Logger
from model import *
import constants as Constants


class RiotChat(ClientXMPP):
	'''
	The RiotChat represents a connection to the Riot XMPP servers in order to
	serve the users with messages, as well as to read any incoming messages.
	'''

	def __init__(self, active_alerter, alerter_model):
		'''
		Constructor
		
		:param active_alerter: The parent alerter for the chat
		:param alerter_model: 
			The database alerter model associated with the bot
		'''
		# Initialises the connection
		ClientXMPP.__init__(self,
						'{}@{}/{}'.format(alerter_model.username,
							Constants.CHAT_SERVER, Constants.CHAT_RESOURCE),
						'AIR_{}'.format(alerter_model.password))

		# Automatically add new friends?
		self.auto_authorize = None
		
		self.auto_subscribe = True
		self.auto_reconnect = True
		self.ssl_version = ssl.PROTOCOL_SSLv3

		# Add the event handlers
		self.add_event_handler('session_start', self.session_start)
		self.add_event_handler('message', self.got_message)
		self.add_event_handler('got_online', self.got_online)
		self.add_event_handler('got_offline', self.got_offline)
		self.add_event_handler('presence_subscribe', self.presence_subscribe)
		self.add_event_handler('presence_unsubscribe',
							self.presence_unsubscribe)
		self.add_event_handler('disconnected', self.disconnected)
		self.add_event_handler('failed_auth', self.failed_auth)

		# Presence change events
		self.add_event_handler('presence_available', self.handle_presence)
		self.add_event_handler('presence_dnd', self.handle_presence)
		self.add_event_handler('presence_xa', self.handle_presence)
		self.add_event_handler('presence_chat', self.handle_presence)
		self.add_event_handler('presence_away', self.handle_presence)

		self.alerter = active_alerter
		self.model = alerter_model

	def start(self):
		'''
		Connects the bot to the chat servers and starts processing messages
		'''
		address = (self.chat_address, Constants.CHAT_ADDRESS_PORT)
		Logger().get().info("Connecting to chat server")

		self.alive = True
		self.connect(address, True, False, True)
		self.process(block=False)

	def stop(self):
		'''
		Disconnects the bot from the chat servers and stops processing messages
		'''
		self.alive = False
		self.disconnect(wait=True)

	def session_start(self, event):
		'''
		Handles the event of the bot connecting to the server
		
		:param event: An event object containing info about the connection
		'''
		try:
			self.send_presence(-1, self.presence_string)
			self.get_roster()
		except IqError as err:
			Logger().get().fatal("An error occurred while getting the roster")
			Logger().get().error(err.iq['error']['condition'])
			self.disconnect(True)
		except IqTimeout:
			Logger().get().fatal("Connection to chat servers timed out")
			self.disconnect(True)
		except Exception as err:
			Logger().get().fatal("An error occurred while getting the roster")
			Logger().get().exception(err)
			self.disconnect(True)

	def got_message(self, message):
		'''
		Handles the event of an incoming message from the server
		
		:param message: A message object
		'''
		summoner_id = self.get_summoner_id(str(message['from']))
		
		admin_summoner = Setting.get(Setting.key == 'AdminSummoner').value
		
		is_admin = summoner_id == admin_summoner
		
		if(message['type'] in ('chat', 'normal')):
			split = str(message['body']).split(' ')
			
			if is_admin:
				if split[0].lower() == '!online':
					message.reply("Online Users: " + 
						", ".join(self.alerter.online_users)).send()
				elif split[0].lower() == '!message':
					new_split = str(message['body'])[1:].split(' ', 2)
					self.alerter.tracker.\
						global_message(new_split[1].lower(), new_split[2])
						
			else:
				if split[0].lower() == 'hi':
					message.reply("Hi").send()
				elif split[0].lower() == '!restart':
					self.alerter.user_offline(summoner_id)
					self.alerter.user_online(summoner_id, True)
				else:
					summoner = self.alerter.get_user(summoner_id).summoner
					forward = "{}: {}".format(summoner.user.twitchusername,
						str(message['body']))
					Logger().get().info('Received Message: '+ forward)
					self.new_message(admin_summoner, forward)

	def got_online(self, presence):
		'''
		Handles the event of a user connecting to the chat
		
		:param presence: A presence object for the new user
		'''
		summoner_id = self.get_summoner_id(str(presence['from']))
		if(summoner_id != str(self.model.summonerid)):
			self.alerter.user_online(summoner_id)

	def got_offline(self, presence):
		'''
		Handles the event of a user disconnecting from the chat
		
		:param presence: A presence object about the disconnected user
		'''
		summoner_id = self.get_summoner_id(str(presence['from']))
		if(summoner_id != self.model.summonerid):
			self.alerter.user_offline(summoner_id)

	def presence_subscribe(self, presence):
		'''
		Handles the event of a user requesting friendship
		
		:param presence: The new subscribe presence of the user
		'''
		summoner_id = self.get_summoner_id(str(presence['from']))
		self.alerter.summoner_friend_requested(summoner_id, presence['from'])

	def presence_unsubscribe(self, presence):
		'''
		Handles the event of a user declining a friendship
		
		:param presence: The new unsubscribe presence of the user
		'''
		summoner_id = self.get_summoner_id(str(presence['from']))
		self.alerter.summoner_friend_deleted(summoner_id)

	def disconnected(self):
		'''
		Handles the event of the bot disconnecting from the server
		'''
		if self.alive:
			self.alerter.Restart()

	def failed_auth(self, error):
		'''
		Handles the event of the bot failing to connect to the servers
		
		:param error: The error containing information about the failed auth
		'''
		Logger().get().fatal("Failed to authenticate to the servers")
		Logger().get().exception(error)
		self.alive = False

	def handle_presence(self, presence):
		'''
		Handles the event of a user changing their presence
		
		:parama presence: The new presence of the user
		'''
		self.roster[presence['to'].bare][presence['from'].bare].handle_available(presence)
		summoner_id = self.get_summoner_id(str(presence['from']))
		self.alerter.summoner_changed_presence(summoner_id, presence)

	def new_message(self, summoner_id, message):
		'''
		Sends a message to a particular summoner
		
		:param summoner_id: The summoner ID of the recipient
		:param message: The message to be sent
		'''
		self.send_message(mto=self.get_jid(summoner_id), 
			mbody=message, mtype='chat')

	def get_summoner_id(self, jid):
		'''	Returns the summoner ID after extracting from the JID
		
		:param jid: The JID from which to extract the summoner ID
		'''
		return jid.split('@', 1)[0].replace('sum', '')

	def get_jid(self, summoner_id):
		''' Returns an XMPP jid from a given summoner ID
		
		:param summoner_id: The summoner ID to incorporate into the JID
		'''
		return 'sum{}@{}'.format(str(summoner_id), Constants.CHAT_SERVER)

	@property
	def chat_address(self):
		return Constants.CHAT_ADDRESS.format(
			region=self.model.region.regionchat)

	@property
	def presence_string(self):
		return('<body><profileIcon>594</profileIcon><level>30</level><wins>' +\
				'729</wins><leaves>0</leaves><odinWins>10</odinWins>' + \
				'<odinLeaves>0</odinLeaves><queueType /><rankedLosses>0' + \
				'</rankedLosses><rankedRating>0</rankedRating><tier>' + \
				'CHALLENGER</tier><rankedSoloRestricted>false' + \
				'</rankedSoloRestricted><rankedLeagueName>Redback&apos;s ' + \
				'Skills</rankedLeagueName><rankedLeagueDivision>I' + \
				'</rankedLeagueDivision><rankedLeagueTier>MASTER' + \
				'</rankedLeagueTier><rankedLeagueQueue>RANKED_SOLO_5x5' + \
				'</rankedLeagueQueue><rankedWins>1083</rankedWins>' + \
				'<gameStatus>outOfGame</gameStatus><statusMsg>' + \
				self.model.message + '</statusMsg></body>')
