from mongoengine import *


class User(Document):
    name = StringField(required=True, unique=True)
    password = StringField(required=True)
    group = StringField()
    sources = ListField()
    targets = ListField()