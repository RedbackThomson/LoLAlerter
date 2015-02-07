'''
	LoLAlerter: Every LoL partner's pal
	Copyright (C) 2015 Redback
	This file is part of LoLAlerter
'''

from alerterredis import AlerterRedis
from dbtrack import DBTracker
from logger import Logger
from settings import Settings
from twitch.subtrack import UnsubTracker
from twitch.twitchchat import TwitchChat


class LoLAlerter(object):
	def __init__(self):
		Logger().get().info("Started LoLAlerter")
		
		AlerterRedis.configure(Settings.redis())
		AlerterRedis().clear()
		
		self.chat = TwitchChat()
		
		unsub = UnsubTracker()
		unsub.start()
		
		dbtracker = DBTracker(self)
		dbtracker.start()

if __name__ == '__main__':
	LoLAlerter()