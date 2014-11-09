import hashlib
from mongoengine import *


class User(Document):
    name = StringField(required=True, unique=True)
    password = StringField(required=True)
    group = StringField()
    news_sources = DictField()
    news_targets = DictField()
    twitter_sources = DictField()
    twitter_targets = DictField()

if __name__ == '__main__':
    # connects to the database
    host = "ds035260.mongolab.com:35260"
    dbName = "userinterface"
    username = "admin"
    password = "admin"
    conn = connect(dbName, host=host, username=username, password=password)
    user = User.objects(name='guest').first()
    print user.news_targets.values()
    print user.news_targets.keys()
    # # prompt in the commandline 
    # name = raw_input("Enter name: ")
    # password = raw_input("Enter pass: ")
    # group = raw_input("Enter Group: ")
    # news_sources ={}
    # news_targets ={}
    # twitter_sources = {}
    # twitter_targets = {}

    # news_sources["aljazeera"] = "www.aljazeera.com"
    # news_sources["haaretz"] = "www.haaretz.com" 
    # news_targets["bbc"] = "www.bbc.com"
    # news_targets["cnn"] = "www.cnn.com"
    # twitter_sources["twitter 1"] = "www.t1.com"
    # twitter_sources["twitter 2"] = "www.t2.com"
    # twitter_targets["twitter 3"] = "www.t3.com"
    # twitter_targets["twitter 4"] = "www.t4.com"
    # p = hashlib.md5()
    # p.update(password)
    # User(name = name, 
    #     password = p.hexdigest(), 
    #     group = group, 
    #     news_sources = news_sources, 
    #     news_targets = news_targets, 
    #     twitter_sources = twitter_sources,  
    #     twitter_targets = twitter_targets).save()