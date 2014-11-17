from mongoengine import *
from tweet import Tweet

class TwitterAccount(Document):
	name = StringField()
	screen_name = StringField()
	tweets = ListField()
