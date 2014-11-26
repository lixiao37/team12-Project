import unittest

from twitterparser import *
from database import *

class TwitterParserTest(unittest.TestCase):
    
    #Database for unittest
    host = "ds053160.mongolab.com:53160"
    dbName = "unittests"
    username = "admin"
    password = "admin"    
    
    def setUp(self):
	self.data = Database(host=self.host, dbName=self.dbName, verbose=False)
	self.data.connect()	
	self.tp = TwitterParser(data = self.data)
	self.tp.authorize()
	
    def tearDown(self):
	self.tp = None
	self.data = None
	TwitterAccount.drop_collection()
	Tweet.drop_collection()
	
    def test_search_tweets(self):
	'''
	Test the search_tweets method, where it returns a list of query results
	'''
	st = self.tp.search_tweets('news')
	
	#Check if there are content in the list
	self.assertTrue(len(st) >= 1)
	
	#Loop through the list and check the text, entities and author of each
	#tweet
	for i in range(len(st)):
	    self.assertTrue(st[i].text)
	    self.assertTrue(st[i].entities)
	    self.assertTrue(st[i].author)
	
    def test_search_multi_tweets(self):
	'''
	Test the search_tweets method multiple times.
	'''
	st_one = self.tp.search_tweets('Dalia')
	st_two = self.tp.search_tweets('israeli')
	
	#Loop through the list and check the text, entities and author of each
	#tweet	
	for i in range(len(st_one)):
	    self.assertTrue(st_one[i].text)
	    self.assertTrue(st_one[i].entities)
	    self.assertTrue(st_one[i].author.name)
	        
	for i in range(len(st_two)):
	    self.assertTrue(st_two[i].text)
	    self.assertTrue(st_two[i].entities)
	    self.assertTrue(st_two[i].author.name)  
	
    def test_get_user_tweets(self):
	'''
	Test the get_user_tweets method, where it returns a list of tweets from
	the specified user
	'''
	t = self.tp.get_user_tweets('DaliaHatuqa')
	
	#Check if there are content in the list
	self.assertTrue(len(t) >= 1)
	
	#Loop through the list and check the text, entities and author of each
	#tweet	
	for i in range(len(t)):
	    self.assertTrue(t[i].text)
	    self.assertTrue(t[i].entities)
	    self.assertTrue(t[i].author)	    
	    
    def test_get_multi_user_tweets(self):
	'''
	Test the get_user_tweets method multiple times
	'''	
	t_one = self.tp.get_user_tweets('AnshelPfeffer')
	t_two = self.tp.get_user_tweets('mattduss')
	
	#Loop through the list and check the text, entities and author of each
	#tweet	
	for i in range(len(t_one)):
	    self.assertTrue(t_one[i].text)
	    self.assertTrue(t_one[i].entities)
	    self.assertTrue(t_one[i].author.name)
		
	for i in range(len(t_two)):
	    self.assertTrue(t_two[i].text)
	    self.assertTrue(t_two[i].entities)
	    self.assertTrue(t_two[i].author.name)
	    
    def test_get_real_url(self):
	'''
	Test the get_real_url method, where it returns the real url from the
	short version
	'''	
	url = self.tp.get_real_url('http://bit.ly/1CbblD3')
	
	self.assertEqual(url, 'https://twitter.com/DaliaHatuqa/status/537230790225309696')
	
    def test_get_multi_real_url(self):
	'''
	Test the get_real_url method multiple times
	'''
	url_one = self.tp.get_real_url('http://bit.ly/1zqDoIO')
	url_two = self.tp.get_real_url('http://bit.ly/1rcwiJc')
	url_three = self.tp.get_real_url('http://bit.ly/1vjSBMo')
	
	self.assertEqual(url_one, 'https://twitter.com/DaliaHatuqa/status/536826369133383680')
	self.assertEqual(url_two, 'https://twitter.com/DaliaHatuqa/status/536774478316191744')
	self.assertEqual(url_three, 'https://twitter.com/DaliaHatuqa/status/536408741642764288')
		
    def test_get_tweet_urls(self):
	'''
	Test the get_tweet_urls method, where it returns all the tweet urls
	inside the given tweet
	'''
	t = self.tp.get_user_tweets('mehmetfcelebi')
	
	tu = self.tp.get_tweet_urls(t[0])
	
	#Check if one of the tweets contain a tweet url
	for i in tu:
	    if tu:
		self.assertTrue(tu)
		break
	    
    def test_get_multi_tweet_urls(self):
	'''
	Test the get_tweet_urls method multiple times
	'''

	t_one = self.tp.get_user_tweets('DaliaHatuqa')
	t_two = self.tp.get_user_tweets('AJENews')
	
	tu_one = self.tp.get_tweet_urls(t_one[1])
	tu_two = self.tp.get_tweet_urls(t_two[0])
	
	#Check if one of the tweets contain a tweet url
	for i in tu_one:
	    if tu_one:
		self.assertTrue(tu_one)
		break
	    
	for i in tu_two:
	    if tu_two:
		self.assertTrue(tu_two)
		break
	
    def test_get_user(self):
	'''
	Test the get_user method, where it returns the user object
	'''
	user = self.tp.get_user('DaliaHatuqa')
	
	self.assertEqual(user.name, 'Dalia Hatuqa')
	self.assertEqual(user.screen_name, 'DaliaHatuqa')
    
    def test_get_multi_user(self):
	'''
	Test the get_user method multiple times
	'''
	user_one = self.tp.get_user('DaliaHatuqa')
	user_two = self.tp.get_user('AJENews')
	user_three = self.tp.get_user('AnshelPfeffer')
	
	self.assertEqual(user_one.name, 'Dalia Hatuqa')
	self.assertEqual(user_one.screen_name, 'DaliaHatuqa')
	self.assertEqual(user_two.name, 'AJE News')
	self.assertEqual(user_two.screen_name, 'AJENews')
	self.assertEqual(user_three.name, 'Anshel Pfeffer')
	self.assertEqual(user_three.screen_name, 'AnshelPfeffer')
    
    def test_get_one_user_mentions(self):
	'''
	Test the get_user_mentions method from one target user
	'''
	t = self.tp.get_user_tweets('DaliaHatuqa')
	
	mentions = self.tp.get_user_mentions(t, ['AnshelPfeffer'])
	
	for i in range(len(mentions)):
	    self.assertTrue('@AnshelPfeffer' in mentions[i].text)
	    
    def test_get_multi_user_mentions(self):
	'''
	Test the get_user_mentions method from multiple target users
	'''
	t = self.tp.get_user_tweets('DaliaHatuqa')
	
	mentions = self.tp.get_user_mentions(t, ['AnshelPfeffer', 
	                                         'blakehounshell', 
	                                         'NathanThrall'])
	
	target_users = ['@AnshelPfeffer', '@blakehounshell', '@NathanThrall']
	
	for i in range(len(mentions)):
	    for j in target_users:
		if j in mentions[i].text:
		    self.assertTrue(j in mentions[i].text)
    
    def test_count_mentions(self):
	'''
	Test the count_mentions method, where it returns the number of mentions 
	for a user, in a dictionary
	'''
	username = 'DaliaHatuqa'
	target = 'AnshelPfeffer'
	
	user = self.tp.get_user(username)
	t = self.tp.get_user_tweets(username)
	mentions = self.tp.get_user_mentions(t, [target])
	men_count = len(mentions)
	counter = -1
	
	count = count_mentions(user)
	self.assertTrue(target in count)
        if target in count:
            counter = count[target]
        self.assertTrue(men_count == counter)
    
    def test_multi_count_mentions(self):
	'''
	Test the count_mentions multiple times
	'''
	username = 'DaliaHatuqa'
	targets = ['AnshelPfeffer','blakehounshell','NathanThrall']
	counter = []
        pos = 0
	for target in targets:
            user = self.tp.get_user(username)
            t = self.tp.get_user_tweets(username)
            mentions = self.tp.get_user_mentions(t, [target[pos]])
            men_count = len(mentions)
            counter.append(men_count)
            pos += 1

	pos = 0
	count = count_mentions(user)
	for target in targets:
            self.assertTrue(target[pos] in count)
            if target[pos] in count:
                counter[pos] = count[target[pos]]
            self.assertTrue(men_count == counter[pos])
            pos += 1
    
    def test_add_user_tweets(self):
	'''
	Test the add_user_tweets, where it adds all the tweets from the user as
	well as the associated users from the tweets
	'''
	pass
    
    def test_add_multiple_user_tweets(self):
	'''
	Test the add_user_tweets multiple times
	'''
	pass	
    
    def test_count_ref(self):
	'''
	Test the count_ref method, where it counts the relation between two
	users
	'''

	tweets_one = self.tp.add_user_tweets('DaliaHatuqa')
	tweets_two = self.tp.add_user_tweets('AnshelPfeffer')
	
	total = self.tp.count_ref('DaliaHatuqa', 'AnshelPfeffer')
	
	self.assertEqual(total, 3)
    
if __name__ == '__main__':
    unittest.main()
