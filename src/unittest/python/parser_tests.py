import unittest

from parser import *
from database import *

class TestGetMetaData(unittest.TestCase):

	#Database for unittest
	host = "ds053160.mongolab.com:53160"
	dbName = "unittests"

	def setUp(self):
		self.p = Parser()
		self.data = Database(host=self.host, dbName=self.dbName, verbose=False)
		self.data.connect()
		self.meta_data_one = {}
		self.meta_data_one["author"] = 'Al Jazeera and agencies'
		self.meta_data_one["url"] = 'http://www.aljazeera.com/news/middleeast/2014/11/syria-seriously-studying-un-truce-proposal-2014111118514613822.html'
		self.meta_data_one["title"] = "Syria 'seriously studying' UN truce proposal"

	def tearDown(self):
		self.p = None
		self.data = None
		self.meta_data_one = None

	def test_exist_meta(self):
		'''Check if the five meta info exists'''
		meta_data = self.p.get_meta_data('http://www.aljazeera.com/news/middleeast/2014/11/syria-seriously-studying-un-truce-proposal-2014111118514613822.html')
		self.assertTrue(meta_data['author'])
		self.assertTrue(meta_data['url'])
		self.assertTrue(meta_data['title'])
		self.assertTrue(meta_data['last_modified_date'])
		self.assertTrue(meta_data['html'])

	def test_compare_meta_data(self):
		'''Compare a recent meta data with a pre defined meta data'''
		meta_data = self.p.get_meta_data('http://www.aljazeera.com/news/middleeast/2014/11/syria-seriously-studying-un-truce-proposal-2014111118514613822.html')
		self.assertEqual(meta_data['author'], self.meta_data_one['author'])
		self.assertEqual(meta_data['url'], self.meta_data_one['url'])
		self.assertEqual(meta_data['title'], self.meta_data_one['title'])


class TestSearchArticle(unittest.TestCase):

	#Database for unittest
	host = "ds053160.mongolab.com:53160"
	dbName = "unittests"

	def setUp(self):
		self.p = Parser()
		self.data = Database(host=self.host, dbName=self.dbName, verbose=False)
		self.data.connect()

	def tearDown(self):
		self.p = None
		self.data = None

	def test_exist_article(self):
		'''Check to ensure that there is at least one article'''
		url_list = self.p.searchArticle('haaretz', 'www.cnn.com')
		self.assertTrue(len(url_list) >= 1)

	def test_duplicate_article(self):
		'''Check to see if there are duplicate articles'''
		url_list = self.p.searchArticle('haaretz', 'www.cnn.com')
		seen = set()
		seen_add = seen.add
		seen_twice = set(x for x in url_list if x in seen or seen_add(x))
		self.assertEqual(seen_twice, set([]))


if __name__ == '__main__':
	unittest.main()