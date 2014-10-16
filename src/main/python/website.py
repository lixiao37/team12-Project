from mongoengine import *


class Website(Document):
	name = StringField(required=True, unique=True)
	homepage_url = StringField()
	country = StringField()