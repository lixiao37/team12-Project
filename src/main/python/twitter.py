from mongoengine import *


class TwitterAccount(Document):
	name = StringField(required=True)
	screen_name = StringField(required=True, unique=True)
	tweets = ListField()


class Tweet(Document):
	text = StringField(unique=True)
	entities = DictField()
	author = ReferenceField(TwitterAccount, reverse_delete_rule=CASCADE, 
							required=True)
	retweeted = BooleanField()
	retweet_author = ReferenceField(TwitterAccount, reverse_delete_rule=CASCADE)
	retweet = ReferenceField('self', reverse_delete_rule=CASCADE)
