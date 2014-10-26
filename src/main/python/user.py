import hashlib
from mongoengine import *


class User(Document):
    name = StringField(required=True, unique=True)
    password = StringField(required=True)
    group = StringField()
    news_sources = ListField()
    news_targets = ListField()
    twitter_sources = ListField()
    twitter_targets = ListField()

if __name__ == '__main__':
    # connects to the database
    host = "ds035260.mongolab.com:35260"
    dbName = "userinterface"
    username = "admin"
    password = "admin"
    conn = connect(dbName, host=host, username=username, password=password)

    # prompt in the commandline 
    name = raw_input("Enter name: ")
    password = raw_input("Enter pass: ")
    group = raw_input("Enter Group: ")
    news_sources = ["aljazeera", "haaretz"]
    news_targets = ["bbc", "cnn"]
    twitter_sources = ["twitter 1", "twitter 2"]
    twitter_targets = ["twitter 3", "twitter 4"]
    p = hashlib.md5()
    p.update(password)
    User(name = name, 
        password = p.hexdigest(), 
        group = group, 
        news_sources = news_sources, 
        news_targets = news_targets, 
        twitter_sources = twitter_sources, 
        twitter_targets = twitter_targets).save()