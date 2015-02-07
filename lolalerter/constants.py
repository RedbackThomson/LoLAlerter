'''
	LoLAlerter: Every LoL partner's pal
	Copyright (C) 2015 Redback
	This file is part of LoLAlerter
'''

CHAT_ADDRESS, CHAT_ADDRESS_PORT = 'chat.{region}.lol.riotgames.com', 5223
CHAT_SERVER, CHAT_RESOURCE = 'pvp.net', 'lolalerter'

TWITCH_HOST, TWITCH_PORT = 'irc.twitch.tv', 6667

SUBSCRIBER_URI = 'https://api.twitch.tv/kraken/channels/{username}/'+\
	'subscriptions?direction=DESC&limit={limit}&offset={offset}&'+\
	'oauth_token={token}&_={timestamp}'

TWITCHALERTS_URI = 'http://www.twitchalerts.com/api/donations?'+\
	'access_token={token}'
	
ERROR_MESSAGE = 'Oops! Something went wrong! Please tweet @Redback93 with ' +\
	'the reference ID: {ref}. Type !restart to attempt to restart the bot.'
	
ADDED_SUCCESS = 'Summoner successfully added! Welcome to LoLAlerter.'
INACTIVE_RESTART = 'Your LoLAlerter subscription is not active. '+\
	'Press !restart to retry'
INACTIVE_NOW_ACTIVE = 'LoLAlerter has successfully restarted and is active.'

RESUB_FLAG = '[Resub] '
NEW_SUBSCRIBER = '{} has just subscribed!'
RESUB_SUBSCRIBER = RESUB_FLAG + NEW_SUBSCRIBER
 
NEW_DONATION = 'Donation of ${} from {}'