import hashlib
from mongoengine import *


class User(Document):
    name = StringField(required=True, unique=True)
    password = StringField(required=True)
    group = StringField()
    news_sources = DictField()
    news_targets = DictField()
    twitter_sources = ListField()
    twitter_targets = ListField()

if __name__ == '__main__':
    pass
