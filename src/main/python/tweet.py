from mongoengine import *
from twitteraccount import TwitterAccount

class Tweet(Document):
	text = StringField()
	author = ReferenceField(TwitterAccount, reverse_delete_rule=CASCADE)
	retweet = ReferenceField(Tweet)
