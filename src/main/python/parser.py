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

	def add_to_database(self, article_meta=None, website_meta=None,
						citation_meta=None):
		'''API function to add parsed data into the database'''
		art = Article(
				title=article_meta.get("title"),
				author=article_meta.get("author"),
				last_modified_date=article_meta.get("last_modified_date"),
				html=article_meta.get("html"),
				url=article_meta.get("url"),
				website=self.db_website_object
					)
		status = art.save()
		if status:
			print "Article Saved Into Database"
		else:
			print "ERROR: Article did not save successfully ...!"

if __name__ == '__main__':
	pass

