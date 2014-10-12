from mongoengine import *

class Article(Document):
	title = StringField()
	author = StringField()
	last_modified_date = DateTimeField()
	html = BinaryField()
	text = StringField()
	website = ReferenceField(Website, reverse_delete_rule=CASCADE)
	url = URLField()
	citations = ListField()
	quotes = ListField()

class Citation(Document):
	text = StringField()
	author = StringField()
	article = ReferenceField(Article, reverse_delete_rule=CASCADE)
