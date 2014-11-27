from mongoengine import *
from website import *
import datetime


class Article(Document):
    title = StringField(required=True)
    author = StringField()
    last_modified_date = StringField()
    time_parsed = DateTimeField(default=datetime.datetime.now)
    html = StringField()
    url = URLField(required=True, unique=True)
    website = ReferenceField(Website, reverse_delete_rule=CASCADE)
    text = StringField()
    citations = ListField()
    screenshot = BinaryField()

if __name__ == '__main__':
    pass
    # connects to the database
    # host = "ds035260.mongolab.com:35260"
    # dbName = "userinterface"
    # username = "admin"
    # password = "admin"
    # conn = connect(dbName, host=host, username=username, password=password)

    # title = raw_input("Enter title: ")
    # url = raw_input("Enter unique url: ")
    # homepage_url = raw_input("Enter homepage_url: ")
    # website = Website.objects(homepage_url=homepage_url)[0]

    # # creates article in db
    # Article(title = title,
    #     url = url,
    #     homepage_url = homepage_url,
    #     website = website).save()
