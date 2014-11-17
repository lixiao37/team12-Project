from mongoengine import *
from tweet import Tweet

class TwitterAccount(Document):
	name = StringField(required=True)
	screen_name = StringField(required=True)
	tweets = ListField()
