import unittest

from parser import *

class ParserTest (unittest.TestCase):

	#Database for unittest
	host = "ds053160.mongolab.com:53160"
	dbName = "unittests"

	def setUp(self):
		self.parse = Parser(host=self.host, dbName=self.dbName, verbose=False)

	def tearDown(self):
		self.parse = None
		#reset the database for each test-cases
		Website.drop_collection()
		Article.drop_collection()
		Citation.drop_collection()

	def test_add_article(self):
		website = Website(name="CNN", homepage_url="http://www.cnn.com", 
						  country="USA")
		website.save()

		article_meta = {}
		article_meta["title"] = "Article-1"
		article_meta["author"] = "John Smith"
		article_meta["url"] = "http://www.article-1.com"

		art = self.parse.add_article(article_meta, website)

		#check if the data was inputted correctly
		self.assertEqual(art.title, article_meta["title"])
		self.assertEqual(art.author, article_meta["author"])
		self.assertEqual(art.url, article_meta["url"])

	def test_add_website(self):
		pass

	def test_add_citation(self):
		pass

if __name__ == '__main__':
	unittest.main()