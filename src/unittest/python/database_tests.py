import unittest

from database import *

class DatabaseTest (unittest.TestCase):

	#Database for unittest
	host = "ds053160.mongolab.com:53160"
	dbName = "unittests"
	username = "admin"
	password = "admin"

	def setUp(self):
		self.data = Database(host=self.host, dbName=self.dbName, verbose=False)
		self.assertFalse(self.data.isConnect())
		self.data.connect(username=self.username, password=self.password)

	def tearDown(self):
		self.data = None
		#reset the database for each test-cases
		Website.drop_collection()
		Article.drop_collection()
		Citation.drop_collection()

	def test_add_article(self):
		'''
		Test the add_article method, that adds article data into the database
		'''
		website = Website(name="CNN", homepage_url="http://www.cnn.com")
		website.save()

		article_meta = {}
		article_meta["title"] = "Article-1"
		article_meta["author"] = "John Smith"
		article_meta["url"] = "http://www.article-1.com"

		art = self.data.add_article(article_meta, website)

		#check if the data was inputted correctly
		self.assertEqual(art.title, article_meta["title"])
		self.assertEqual(art.author, article_meta["author"])
		self.assertEqual(art.url, article_meta["url"])

	def test_add_article_duplicate(self):
		'''
		Test the add_article method, by adding same article twice
		'''
		website = Website(name="CNN", homepage_url="http://www.cnn.com")
		website.save()

		article_meta = {}
		article_meta["title"] = "Article-1"
		article_meta["author"] = "John Smith"
		article_meta["url"] = "http://www.article-1.com"

		art = self.data.add_article(article_meta, website)
		art_two = self.data.add_article(article_meta, website)

		#check if both articles are the actually the same articles
		self.assertEqual(art.title, art_two.title)
		self.assertEqual(art.author, art_two.author)
		self.assertEqual(art.url, art_two.url)
		self.assertEqual(art.id, art_two.id)

	def test_add_website(self):
		'''
		Test the add_website method, that adds website data into the database
		'''
		website_meta = {}
		website_meta["name"] = "CNN"
		website_meta["homepage_url"] = "http://www.article-1.com"

		web = self.data.add_website(website_meta)

		self.assertEqual(web.name, website_meta["name"])
		self.assertEqual(web.homepage_url, website_meta["homepage_url"])

	def test_add_website_duplicate(self):
		'''
		Test the add_website method, add duplicate websites
		'''
		website_meta = {}
		website_meta["name"] = "CNN"
		website_meta["homepage_url"] = "http://www.article-1.com"

		web = self.data.add_website(website_meta)
		web_two = self.data.add_website(website_meta)

		self.assertEqual(web.name, web_two.name)
		self.assertEqual(web.homepage_url, web_two.homepage_url)

	def test_add_citation(self):
		'''
		Test the add_citation method, that adds citation data into the database
		'''
		website = Website(name="CNN", homepage_url="http://www.cnn.com")
		website.save()

		target_website = Website(name="Haaretz",
								 homepage_url="http://www.haaretz.com")
		target_website.save()

		article_meta = {}
		article_meta["title"] = "Article-1"
		article_meta["author"] = "John Smith"
		article_meta["url"] = "http://www.article-1.com"

		art = self.data.add_article(article_meta, website)

		target_article_meta = {}
		target_article_meta["title"] = "Article-2"
		target_article_meta["author"] = "John Smith"
		target_article_meta["url"] = "http://www.article-2.com"

		target_art = self.data.add_article(target_article_meta, target_website)

		citation_meta = {}
		citation_meta["text"] = "Haaretz said that people need to play football"
		citation_meta["article"] = art
		citation_meta["target_article"] = target_art
		citation_meta["target_name"] = "Haaretz"

		cite = self.data.add_citation(citation_meta)

		self.assertEqual(cite.text, citation_meta["text"])
		self.assertEqual(cite.article, citation_meta["article"])
		self.assertEqual(cite.target_article, citation_meta["target_article"])
		self.assertEqual(cite.target_name, citation_meta["target_name"])

