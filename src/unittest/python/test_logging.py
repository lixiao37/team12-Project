import unittest

from parser import *
from twitterparser import *
from database import *

class ParserLoggingTest(unittest.TestCase):
    
    #Database for unittest
    host = "ds053160.mongolab.com:53160"
    dbName = "unittests"
    
    #Set up the parser and create the log message
    p = Parser(host, dbName)
    data = Database(host, dbName, verbose = False)
    data.connect()
    sources = {'Al Jazeera' : 'www.aljazeera.com'}
    targets = {'Ahram' : 'www.english.ahram.org.eg'}        
    p.run(sources, targets)    
    
    def setUp(self):
        '''Set up the log by opening it'''
        self.log = open('beta.log', 'r')        
        
    def tearDown(self):
        '''Close the file after testing'''
        self.log.close()
        
    def test_log_database_connect(self):
        '''Test if in the log, the connection was successful to the database'''
        self.assertTrue('database - INFO - Connected to the "unittests" Database!' in self.log.read())
    
    def test_log_started_parsing(self):
        '''Test if in the log, the parser starting parsing to the database'''
        self.assertTrue('parser - INFO - Started Website Parsing' in self.log.read())   
        
    def test_log_ended_parsing(self):
        '''Test if in the log, the parser finished parsing to the database'''
        self.assertTrue('parser - INFO - Done Parsing Websites' in self.log.read())
        
    def test_log_check_error(self):
        '''Test if in the log, there are no errors detected'''
        self.assertFalse('ERROR' in self.log.read())
        
class TwitterParserLoggingTest(unittest.TestCase):
    
    #Database for unittest
    host = "ds053160.mongolab.com:53160"
    dbName = "unittests" 
    
    #Set up the twitter parser and create the log message
    tp = TwitterParser()
    data = Database(host, dbName, verbose = False)
    data.connect()
    tp.authorize()
    people = ["DaliaHatuqa"]
    tp.run(people)           
    
    def setUp(self):
        '''Set up the log by opening it'''
        self.log = open('beta.log', 'r')        
        
    def tearDown(self):
        '''Close the file after testing'''
        self.log.close()    
                
    def test_authorize_twitter(self):
        '''Test if in the log, the twitter parser is authorized by the parser'''
        self.assertTrue('twitterparser - INFO - Authorized with Twitter' in self.log.read())
        
    def test_started_crawler(self):
        '''Test if in the log, the twitter parser started parsing'''
        self.assertTrue('twitterparser - INFO - Started Twitter Crawler' in self.log.read())
        
    def test_finished_crawler(self):
        '''Test if in the log, the twitter parser finished parsing'''
        self.assertTrue('twitterparser - INFO - Done Twitter Crawler' in self.log.read())
        
    def test_log_check_error(self):
        '''Test if in the log, there are no errors detected'''
        self.assertFalse('ERROR' in self.log.read())
        
if __name__ == '__main__':
    unittest.main()