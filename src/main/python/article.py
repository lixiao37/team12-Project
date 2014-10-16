from mongoengine import *
from website import *


class Article(Document):
	title = StringField(required=True)
	author = StringField()
	last_modified_date = DateTimeField()
	html = StringField()
	url = URLField(required=True, unique=True)
	website = ReferenceField(Website, reverse_delete_rule=CASCADE)
	text = StringField()
	citations = ListField()
	quotes = ListField()