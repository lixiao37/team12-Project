import hashlib
from mongoengine import *


class User(Document):
    name = StringField(required=True, unique=True)
    password = StringField(required=True)
    group = StringField()
    sources = ListField()
    targets = ListField()

if __name__ == '__main__':
    host = "ds035260.mongolab.com:35260"
    dbName = "userinterface"
    username = "admin"
    password = "admin"
    conn = connect(dbName, host=host, username=username,
                        password=password)
    name = raw_input("Enter name: ")
    password = raw_input("Enter pass: ")
    group = raw_input("Enter Group: ")
    sources = ["aljazeera", "haaretz", "zhen's sources"]
    targets = ["bbc", "cnn"]
    p = hashlib.md5()
    p.update(password)
    User(name=name, password=p.hexdigest(), group=group, sources=sources, targets=targets).save()