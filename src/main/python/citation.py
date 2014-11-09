from mongoengine import *
from article import Article


class Citation(Document):
	text = StringField()
	article = ReferenceField(Article, reverse_delete_rule=CASCADE)
	target_article = ReferenceField(Article, reverse_delete_rule=CASCADE)
    target_name = StringField()

if __name__ == '__main__':
    # connects to the database
    host = "ds035260.mongolab.com:35260"
    dbName = "userinterface"
    username = "admin"
    password = "admin"
    conn = connect(dbName, host=host, username=username, password=password)
    
    original_url = 'http://www.bbc.com/food'

    article = Article.objects(url = original_url)[0]
    target_article = Article.objects(url = 'http://metronews.ca/milk')[0]

    Citation(text = 'food to milk',
    	article = article,
    	target_article = target_article).save()
    
    article.citations.append(Citation.objects(text = 'food to milk')[0])
    article.save()
