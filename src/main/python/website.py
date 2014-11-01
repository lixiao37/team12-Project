from mongoengine import *


class Website(Document):
	name = StringField(required=True, unique=True)
	homepage_url = StringField()
	country = StringField()

if __name__ == '__main__':
    # connects to the database
    host = "ds035260.mongolab.com:35260"
    dbName = "userinterface"
    username = "admin"
    password = "admin"
    conn = connect(dbName, host=host, username=username, password=password)

    # prompt in the commandline 
    name = raw_input("Enter name: ")
    homepage_url = raw_input("Enter homepage_url: ")
    
    Website(name = name,
    	homepage_url = homepage_url).save()