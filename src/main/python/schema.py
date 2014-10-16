from mongoengine import *

class Website(Document):
	name = StringField(required=True, unique=True)
	homepage_url = StringField()
	country = StringField()

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

class Citation(Document):
	text = StringField()
	author = StringField()
	article = ReferenceField(Article, reverse_delete_rule=CASCADE)

# Defining the User document's schema
class User(Document):
    name = StringField(required=True, unique=True)
    password = StringField(required=True)
    group = StringField()
    sources = ListField()
    targets = ListField()
