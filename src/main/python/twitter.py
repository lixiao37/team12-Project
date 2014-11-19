from mongoengine import *


class TwitterAccount(Document):
	name = StringField(required=True)
	screen_name = StringField(required=True, unique=True)
	tweets = ListField()


class Tweet(Document):
	text = StringField()
	entities = DictField()
	author = ReferenceField(TwitterAccount, reverse_delete_rule=CASCADE)
	retweet = ReferenceField('self', reverse_delete_rule=CASCADE)
