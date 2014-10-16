from bs4 import BeautifulSoup
from schema import *
import urllib2

class Parser(object):
	"""Generic Parser Class"""

	conn = None
	host = "ds035260.mongolab.com:35260"
	dbName = "userinterface"
	username = "admin"
	password = "admin"

	def __init__(self):
		pass

	def connect(self):
		'''Connect to the database'''
		self.conn = connect(self.dbName, host=self.host, username=self.username,
						password=self.password)
		if self.isConnect():
			print "Connected to the Database"

	def isConnect(self):
		'''Check if connection exists with the database'''
		if self.conn:
			return True
		else:
			return False

	def add_to_database(self, kwargs):
		'''API function to add parsed data into the database'''
		if not self.isConnect():
			self.connect()

		art = Article(	title=kwargs.get("title"),
						author=kwargs.get("author"),
						last_modified_date=kwargs.get("last_modified_date"),
						html=kwargs.get("html"),
						url=kwargs.get("url")
					)
		status = art.save()
		if status:
			print "Article Saved Into Database"
		else:
			print "ERROR: Article did not save successfully ...!"

if __name__ == '__main__':
	pass

