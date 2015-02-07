'''
	LoLAlerter: Every LoL partner's pal
	Copyright (C) 2015 Redback
	This file is part of LoLAlerter
'''

from threading import Thread

from irc.bot import ServerSpec, SingleServerIRCBot

from logger import Logger
from model import *
import constants as Constants


class TwitchChat(SingleServerIRCBot):
	'''
	The TwitchChat is the main powerhorse of the bot. It will be the one to see
	new subscribers and re-subscribers for the user.
	'''

	def __init__(self):
		'''
		Constructor
		'''
		self._channels = []
		self.username = Setting.get(Setting.key=='TwitchUsername').value
		pw = Setting.get(Setting.key=='TwitchAuth').value
		
		spec = ServerSpec(Constants.TWITCH_HOST, Constants.TWITCH_PORT, pw)
		SingleServerIRCBot.__init__(self, [spec], self.username, self.username)
		
		run_thread = Thread(target=self.start)
		run_thread.start()
		
	def on_welcome(self, conn, event):
		'''
		Called by the irc when the bot connects to the server
		
		:param conn: The connection instance
		:param event: The connection event
		'''
		# Send to allow TwitchNotify messages
		conn.send_raw("TWITCHCLIENT 3")
		Logger().get().info("Twitch Chat connected")
		
		for channel in self._channels:
			conn.join('#' + channel.user.twitchusername.lower())
		
	def on_join(self, conn, event):
		'''
		Called by the irc when the bot joins a channel
		
		:param conn: The connection instance
		:param event: The join event
		'''
		user = event.source.nick

		if user == conn.real_nickname:
			Logger().get().info("Chat joined " + event.target)
		
	def on_disconnect(self, conn, event):
		'''
		Called by the irc when the bot disconnects
		
		:param conn: The connection instance
		:param event: The disconnection event
		'''
		Logger().get().error("Twitch Chat disconnected. Reconnecting...");
		
	def on_pubmsg(self, conn, event):
		'''
		Called by the irc when a channel receives a new message
		
		:param conn: The connection instance
		:param event: The public message event
		'''
		message = event.arguments[0]
		user = event.source.nick
		channel_user = self.get_channel(event.target[1:].lower())
		
		# Only track messages from the bot
		if user == "twitchnotify":
			new_sub = message[:message.index(' ')]
			show_resub = (channel_user.user.showresubs == 1)
			
			# Only look for resub messages 
			if 'months in a row' in message:
				channel_user.new_subscriber(new_sub, True)
		
	def get_channel(self, twitch_username):
		'''
		Gets an ActiveUser object given the channel user
		
		:param twitch_username: The TwitchUsername of the ActiveUser
		'''
		return next(x for x in self._channels if x.user.twitchusername 
			== twitch_username)
		
	def add_channel(self, active_user):
		'''
		Adds a user to the list of connected channels
		
		:param active_user: The ActiveUser object which represents the new 
		connection
		'''
		self.remove_channel(active_user)
		self._channels.append(active_user)
		self.connection.join('#' + active_user.user.twitchusername.lower())
		
	def remove_channel(self, active_user):
		'''
		Removes a user from the list of connected channels
		
		:param active_user: The ActiveUser object which represents the old 
		connection
		'''
		to_remove = [x for x in self._channels if x.user.twitchusername ==
			active_user.user.twitchusername]
		for item in to_remove:
			self._channels.remove(item)
			self.connection.part('#'+item.user.twitchusername.lower())