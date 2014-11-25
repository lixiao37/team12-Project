import unittest
import datetime

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
		TwitterAccount.drop_collection()
		Tweet.drop_collection()

	def test_add_article(self):
		'''
		Test the add_article method, that adds article data into the 
		database
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

		#check if both articles are actually the same articles
		self.assertEqual(art.title, art_two.title)
		self.assertEqual(art.author, art_two.author)
		self.assertEqual(art.url, art_two.url)
		self.assertEqual(art.id, art_two.id)

	def test_add_website(self):
		'''
		Test the add_website method, that adds website data into the 
		database
		'''
		website_meta = {}
		website_meta["name"] = "CNN"
		website_meta["homepage_url"] = "http://www.article-1.com"

		web = self.data.add_website(website_meta)

		#check if the data was inputted correctly
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

		#check if both websites are the same
		self.assertEqual(web.name, web_two.name)
		self.assertEqual(web.homepage_url, web_two.homepage_url)

	def test_add_citation(self):
		'''
		Test the add_citation method, that adds citation data into the 
		database
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

		#check if the data was inputted correctly
		self.assertEqual(cite.text, citation_meta["text"])
		self.assertEqual(cite.article, citation_meta["article"])
		self.assertEqual(cite.target_article, citation_meta["target_article"])
		self.assertEqual(cite.target_name, citation_meta["target_name"])

	def test_add_citation_duplicate(self):
		'''
		Test the add_citation method, that adds duplicate citation data 
		into the database
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
		cite_two = self.data.add_citation(citation_meta)

		query = Citation.objects(text=citation_meta["text"],
								 article=citation_meta["article"],
								 target_article=citation_meta["target_article"],
								 target_name=citation_meta["target_name"])

		#make sure that there are no duplicate entries in citation
		self.assertEqual(len(query), 1)
		
	def test_add_twitteraccount(self):
		'''
		Test the add twitter account method, that adds the twitter
		account object into the database
		'''
		twitter_account = TwitterAccount(
		        name = 'Mehdi Ali',
		        screen_name = 'alimehdi1992',
		        tweets = []
		        )
		
		ta = self.data.add_twitteraccount(twitter_account)
		
		#check if the data was inputted correctly
		self.assertEqual(ta.name, 'Mehdi Ali')
		self.assertEqual(ta.screen_name, 'alimehdi1992')
		
	def test_add_multi_twitteraccount(self):
		'''
		Test the add twitter account method multiple times, that adds 
		the twitter account object into the database
		'''
		twitter_account_one = TwitterAccount(
	                name = 'Mehdi Ali',
	                screen_name = 'alimehdi1992',
	                tweets = []
	                )
		
		twitter_account_two = TwitterAccount(
		        name = 'Dalia Hatuqa',
		        screen_name = 'DaliaHatuqa',
		        tweets = []
		        )
		
		ta_one = self.data.add_twitteraccount(twitter_account_one)
		ta_two = self.data.add_twitteraccount(twitter_account_two)
		
		#check if both data were inputted correctly
		self.assertEqual(ta_one.name, 'Mehdi Ali')
		self.assertEqual(ta_one.screen_name, 'alimehdi1992')
		self.assertEqual(ta_two.name, 'Dalia Hatuqa')
		self.assertEqual(ta_two.screen_name, 'DaliaHatuqa')		

	def test_add_tweet(self):
		'''
		Test the add_tweet method, that adds the tweet object into the 
		database
		'''	
		twitter_account = TwitterAccount(
		        name = 'Mehdi Ali',
		        screen_name = 'alimehdi1992',
		        tweets = []
		        )
		
		ta = self.data.add_twitteraccount(twitter_account)
		
		tweet = Tweet(
		        text = "Can't wait #BreakingBadFinale ...!",
		        entities = {u'symbols': [], u'user_mentions': [], u'hashtags': [{u'indices': [11, 29], u'text': u'BreakingBadFinale'}], u'urls': []},
		        author = ta,
		        time_parsed = datetime.datetime.now,
		        created_at = datetime.datetime(2013, 9, 29, 23, 49, 37)
		        )
		
		t = self.data.add_tweet(tweet)
		
		#check if the data was inputted correctly
		self.assertEqual(t.text, "Can't wait #BreakingBadFinale ...!")
		self.assertEqual(t.entities, {u'symbols': [], u'user_mentions': [], u'hashtags': [{u'indices': [11, 29], u'text': u'BreakingBadFinale'}], u'urls': []})
		self.assertEqual(t.author, ta)
		self.assertEqual(t.time_parsed, t.time_parsed)
		self.assertEqual(t.created_at, datetime.datetime(2013, 9, 29, 23, 49, 37))
		
	def test_add_multiple_tweets(self):
		'''
		Test the add_tweet method multiple times, that adds the tweet 
		object into the database
		'''	
		twitter_account = TwitterAccount(
		        name = 'Mehdi Ali',
		        screen_name = 'alimehdi1992',
		        tweets = []
		        )
		
		ta = self.data.add_twitteraccount(twitter_account)
		
		tweet_one = Tweet(
	                text = "Can't wait #BreakingBadFinale ...!",
	                entities = {u'symbols': [], u'user_mentions': [], u'hashtags': [{u'indices': [11, 29], u'text': u'BreakingBadFinale'}], u'urls': []},
	                author = ta,
	                time_parsed = datetime.datetime.now,
	                created_at = datetime.datetime(2013, 9, 29, 23, 49, 37)
	                )
		
		tweet_two = Tweet(
	                text = 'I love Dropbox because it is very fast, I use it to transfer files between my virtual box and my operating system http://t.co/LZXUBxWnDx',
	                entities = {u'symbols': [], u'user_mentions': [], u'hashtags': [], u'urls': [{u'url': u'http://t.co/LZXUBxWnDx', u'indices': [114, 136], u'expanded_url': u'http://db.tt/O1n4DIdK', u'display_url': u'db.tt/O1n4DIdK'}]},
	                author = ta,
	                time_parsed = datetime.datetime.now,
	                created_at = datetime.datetime(2013, 3, 1, 22, 39, 56)
	                )
		
		t_one = self.data.add_tweet(tweet_one)
		t_two = self.data.add_tweet(tweet_two)
		
		#check if both data were inputted correctly
		self.assertEqual(t_one.text, "Can't wait #BreakingBadFinale ...!")
		self.assertEqual(t_one.entities, {u'symbols': [], u'user_mentions': [], u'hashtags': [{u'indices': [11, 29], u'text': u'BreakingBadFinale'}], u'urls': []})
		self.assertEqual(t_one.author, ta)
		self.assertEqual(t_one.time_parsed, t_one.time_parsed)
		self.assertEqual(t_one.created_at, datetime.datetime(2013, 9, 29, 23, 49, 37))	
		
		self.assertEqual(t_two.text, 'I love Dropbox because it is very fast, I use it to transfer files between my virtual box and my operating system http://t.co/LZXUBxWnDx')
		self.assertEqual(t_two.entities, {u'symbols': [], u'user_mentions': [], u'hashtags': [], u'urls': [{u'url': u'http://t.co/LZXUBxWnDx', u'indices': [114, 136], u'expanded_url': u'http://db.tt/O1n4DIdK', u'display_url': u'db.tt/O1n4DIdK'}]})
		self.assertEqual(t_two.author, ta)
		self.assertEqual(t_two.time_parsed, t_two.time_parsed)
		self.assertEqual(t_two.created_at, datetime.datetime(2013, 3, 1, 22, 39, 56))
		
	def test_add_retweet(self):
		pass
	
	def test_add_multiple_retweets(self):
		pass
	
if __name__ == '__main__':
	unittest.main()
