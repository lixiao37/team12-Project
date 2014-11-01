from mongoengine import *
from article import Article


class Citation(Document):
	text = StringField()
	article = ReferenceField(Article, reverse_delete_rule=CASCADE)
	target_article = ReferenceField(Article, reverse_delete_rule=CASCADE)
