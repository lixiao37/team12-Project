from mongoengine import *
from article import Article


class Citation(Document):
	text = StringField()
	author = StringField()
	article = ReferenceField(Article, reverse_delete_rule=CASCADE)