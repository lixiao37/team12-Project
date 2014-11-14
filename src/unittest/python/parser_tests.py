import unittest

from parser import *
from database import *

class GetCitation(unittest.TestCase):

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

	def test_exist_text_citation(self):
		'''
		Check if text citation exists
		'''
		meta_data = self.p.get_meta_data('http://www.aljazeera.com/news/middleeast/2014/10/israeli-knesset-faces-tough-task-over-budget-2014102681237907995.html')
		html = meta_data['html']
		citation = self.p.get_citation(html, 'http://www.haaretz.com/', 'haaretz')
		self.assertTrue(citation)

	def test_exist_href_citation(self):
		'''
		Check if href citation exists
		'''
		meta_data = self.p.get_meta_data('http://www.aljazeera.com/news/middleeast/2014/09/abbas-reveal-plan-at-un-end-occupation-20149235745271899.html')
		html = meta_data['html']
		citation = self.p.get_citation(html, 'http://www.haaretz.com/', 'haaretz')
		self.assertTrue(citation)

	def test_compare_citation(self):
		'''
		Compare two citations from different html. If they are not equal,
		that means get_citation works when run multiple times
		'''
		meta_data_one = self.p.get_meta_data('http://www.aljazeera.com/news/middleeast/2014/09/un-warns-israel-against-relocating-bedouins-201492118213997830.html')
		meta_data_two = self.p.get_meta_data('http://www.aljazeera.com/programmes/listeningpost/2014/08/gazans-reporting-gaza-2014816115633880869.html')
		html_one = meta_data_one['html']
		html_two = meta_data_two['html']
		citation_one = self.p.get_citation(html_one, 'http://www.haaretz.com/', 'Haaretz')
		citation_two = self.p.get_citation(html_two, 'http://www.haaretz.com/', 'Haaretz')
		self.assertNotEqual(citation_one, citation_two)

class TestGetMetaData(unittest.TestCase):

	#Database for unittest
	host = "ds053160.mongolab.com:53160"
	dbName = "unittests"

	def setUp(self):
		self.p = Parser()
		self.data = Database(host=self.host, dbName=self.dbName, verbose=False)
		self.data.connect()
		self.meta_data_source = {}
		self.meta_data_source["author"] = 'Al Jazeera and agencies'
		self.meta_data_source["url"] = 'http://www.aljazeera.com/news/middleeast/2014/11/syria-seriously-studying-un-truce-proposal-2014111118514613822.html'
		self.meta_data_source["title"] = "Syria 'seriously studying' UN truce proposal"
		self.meta_data_target = {}
		self.meta_data_target["author"] = 'Yaniv Kubovich'
		self.meta_data_target["url"] = 'http://www.haaretz.com/news/diplomacy-defense/1.626148'
		self.meta_data_target["title"] = 'Police: Shin Bet keeping us in the dark about East Jerusalem disturbances'

	def tearDown(self):
		self.p = None
		self.data = None
		self.meta_data_source = None
		self.meta_data_target = None

	def test_exist_meta(self):
		'''
		Check if the five meta info exists
		'''
		meta_data = self.p.get_meta_data('http://www.aljazeera.com/news/middleeast/2014/11/syria-seriously-studying-un-truce-proposal-2014111118514613822.html')
		self.assertTrue(meta_data['author'])
		self.assertTrue(meta_data['url'])
		self.assertTrue(meta_data['title'])
		self.assertTrue(meta_data['last_modified_date'])
		self.assertTrue(meta_data['html'])

	def test_compare_meta_data_source(self):
		'''
		Compare a recent meta data from a source website with a pre
		defined meta data
		'''
		meta_data = self.p.get_meta_data('http://www.aljazeera.com/news/middleeast/2014/11/syria-seriously-studying-un-truce-proposal-2014111118514613822.html')
		self.assertEqual(meta_data['url'], self.meta_data_source['url'])
		self.assertEqual(meta_data['title'], self.meta_data_source['title'])

	def test_compare_meta_data_target(self):
		'''
		Compare a recent meta data from a target website with a pre
		defined meta data
		'''
		meta_data = self.p.get_meta_data('http://www.haaretz.com/news/diplomacy-defense/1.626148')
		self.assertEqual(meta_data['url'], self.meta_data_target['url'])
		self.assertEqual(meta_data['title'], self.meta_data_target['title'])

	def test_compare_two_meta_data(self):
		'''
		Collect two meta datas and see if each meta is not equal. This
		ensures that it works when run multiple times
		'''
		meta_data_one = self.p.get_meta_data('http://www.aljazeera.com/news/middleeast/2014/11/jerusalem-tensions-2014111321171627507.html')
		meta_data_two = self.p.get_meta_data('http://www.haaretz.com/news/diplomacy-defense/1.626387')
		self.assertNotEqual(meta_data_one['author'], meta_data_two['author'])
		self.assertNotEqual(meta_data_one['url'], meta_data_two['url'])
		self.assertNotEqual(meta_data_one['title'], meta_data_two['title'])
		self.assertNotEqual(meta_data_one['last_modified_date'], meta_data_two['last_modified_date'])
		self.assertNotEqual(meta_data_one['html'], meta_data_two['html'])


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

	def test_duplicate_article(self):
		'''Check to see if there are duplicate articles'''
		url_list = self.p.searchArticle('Haaretz', 'www.cnn.com')

		#If there are any duplicate websites, add them into seen_twice
		seen = set()
		seen_add = seen.add
		seen_twice = set(x for x in url_list if x in seen or seen_add(x))
		self.assertEqual(seen_twice, set([]))

	def test_compare_article(self):
		'''
		Collect the same two list of articles and check if one of the
		same url exists
		'''
		url_list_one = self.p.searchArticle('haaretz', 'www.cnn.com')
		url_list_two = self.p.searchArticle('haaretz', 'www.cnn.com')

		for url in url_list_one:
			self.assertTrue(url in url_list_two)

if __name__ == '__main__':
	unittest.main()

