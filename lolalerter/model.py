'''
	LoLAlerter: Every LoL partner's pal
	Copyright (C) 2015 Redback
	This file is part of LoLAlerter
'''

from peewee import *  # @UnusedWildImport

from settings import Settings


class UnknownField(object):
    pass

class BaseModel(Model):
    class Meta: 
        settings = Settings.database()
        db = settings['database']
        settings.pop("database", None)

        database = MySQLDatabase(db, **settings)
        
class Region(BaseModel):
    id = PrimaryKeyField(db_column='ID')
    regionchat = CharField(db_column='RegionChat')
    regioncode = CharField(db_column='RegionCode')
    regionname = CharField(db_column='RegionName', unique=True)

    class Meta:
        db_table = 'regions'

class Alerter(BaseModel):
    email = CharField(db_column='Email')
    enabled = IntegerField(db_column='Enabled')
    id = PrimaryKeyField(db_column='ID')
    message = CharField(db_column='Message')
    password = CharField(db_column='Password')
    region = ForeignKeyField(db_column='Region', rel_model=Region, to_field='id')
    summonerid = IntegerField(db_column='SummonerID')
    summonername = CharField(db_column='SummonerName')
    username = CharField(db_column='Username')

    class Meta:
        db_table = 'alerters'

class AlerterFriend(BaseModel):
    alerter = ForeignKeyField(db_column='Alerter', rel_model=Alerter, to_field='id')
    id = PrimaryKeyField(db_column='ID')
    summonerid = IntegerField(db_column='SummonerID')
    timestamp = DateTimeField(db_column='Timestamp')

    class Meta:
        db_table = 'alerter_friends'

class AlerterStatistic(BaseModel):
    alerter = ForeignKeyField(db_column='Alerter', primary_key=True, rel_model=Alerter, to_field='id')
    onlineusers = IntegerField(db_column='OnlineUsers')
    timestamp = DateTimeField(db_column='Timestamp')
    totalsubscribed = IntegerField(db_column='TotalSubscribed')

    class Meta:
        db_table = 'alerter_statistics'

class Notice(BaseModel):
    id = PrimaryKeyField(db_column='ID')
    message = CharField(db_column='Message')
    timestamp = DateTimeField(db_column='Timestamp')

    class Meta:
        db_table = 'notices'

class User(BaseModel):
    apikey = CharField(db_column='APIKey', null=True)
    createdate = DateTimeField(db_column='CreateDate')
    id = PrimaryKeyField(db_column='ID')
    lastnotice = ForeignKeyField(db_column='LastNotice', null=True, rel_model=Notice, to_field='id')
    minimumdonation = FloatField(db_column='MinimumDonation', null=True)
    remembertoken = CharField(db_column='RememberToken', null=True)
    showresubs = IntegerField(db_column='ShowResubs', default=True)
    timestamp = DateTimeField(db_column='Timestamp')
    twitchalertskey = CharField(db_column='TwitchAlertsKey', null=True)
    twitchdisplay = CharField(db_column='TwitchDisplay')
    twitchtoken = CharField(db_column='TwitchToken', null=True)
    twitchusername = CharField(db_column='TwitchUsername', unique=True)

    class Meta:
        db_table = 'users'

class Message(BaseModel):
    inchat = CharField(db_column='InChat', null=True)
    ingame = CharField(db_column='InGame', null=True)
    newdonation = CharField(db_column='NewDonation', null=True)
    user = ForeignKeyField(db_column='User', primary_key=True, rel_model=User, to_field='id')

    class Meta:
        db_table = 'messages'

class Setting(BaseModel):
    key = CharField(db_column='Key', primary_key=True)
    value = CharField(db_column='Value')

    class Meta:
        db_table = 'settings'

class Subscriber(BaseModel):
    active = IntegerField(db_column='Active', default=True)
    adddate = DateTimeField(db_column='AddDate')
    displayname = CharField(db_column='DisplayName')
    id = PrimaryKeyField(db_column='ID')
    timestamp = DateTimeField(db_column='Timestamp')
    twitchid = IntegerField(db_column='TwitchID')
    unsubdate = DateTimeField(db_column='UnsubDate', null=True, default=None)
    user = ForeignKeyField(db_column='User', rel_model=User, to_field='id')
    username = CharField(db_column='Username')

    class Meta:
        db_table = 'subscribers'
        indexes = (
			(('user', 'twitchid'), True)
		)

class SubscriptionPayment(BaseModel):
    expirydate = DateTimeField(db_column='ExpiryDate')
    feeamount = FloatField(db_column='FeeAmount')
    firstname = CharField(db_column='FirstName')
    grossamount = FloatField(db_column='GrossAmount')
    id = PrimaryKeyField(db_column='ID')
    lastname = CharField(db_column='LastName')
    payeremail = CharField(db_column='PayerEmail')
    paymentdate = DateTimeField(db_column='PaymentDate')
    txnid = CharField(db_column='TXNID')
    timestamp = DateTimeField(db_column='Timestamp')
    user = ForeignKeyField(db_column='User', rel_model=User, to_field='id')

    class Meta:
        db_table = 'subscription_payments'

class Summoner(BaseModel):
    alerter = ForeignKeyField(db_column='Alerter', rel_model=Alerter, to_field='id')
    id = PrimaryKeyField(db_column='ID')
    summonerid = IntegerField(db_column='SummonerID')
    summonername = CharField(db_column='SummonerName')
    timestamp = DateTimeField(db_column='Timestamp')
    user = ForeignKeyField(db_column='User', rel_model=User, to_field='id')

    class Meta:
        db_table = 'summoners'

class UserStatistic(BaseModel):
    totalsubscribed = IntegerField(db_column='TotalSubscribed')
    user = ForeignKeyField(db_column='User', primary_key=True, rel_model=User, to_field='id')

    class Meta:
        db_table = 'user_statistics'
        
class ActiveSummoner(BaseModel):
    alerter = ForeignKeyField(db_column='Alerter', rel_model=Alerter, to_field='id')
    id = PrimaryKeyField(db_column='ID')
    summonerid = IntegerField(db_column='SummonerID')
    summonername = CharField(db_column='SummonerName')
    timestamp = DateTimeField(db_column='Timestamp')
    user = ForeignKeyField(db_column='User', rel_model=User, to_field='id')

    class Meta:
        db_table = 'active_summoners'

class ActiveUser(BaseModel):
    apikey = CharField(db_column='APIKey', null=True)
    createdate = DateTimeField(db_column='CreateDate')
    id = PrimaryKeyField(db_column='ID')
    lastnotice = ForeignKeyField(db_column='LastNotice', null=True, rel_model=Notice, to_field='id')
    minimumdonation = FloatField(db_column='MinimumDonation', null=True)
    remembertoken = CharField(db_column='RememberToken', null=True)
    showresubs = IntegerField(db_column='ShowResubs', default=True)
    timestamp = DateTimeField(db_column='Timestamp')
    twitchalertskey = CharField(db_column='TwitchAlertsKey', null=True)
    twitchdisplay = CharField(db_column='TwitchDisplay')
    twitchtoken = CharField(db_column='TwitchToken', null=True)
    twitchusername = CharField(db_column='TwitchUsername', unique=True)

    class Meta:
        db_table = 'active_users'
