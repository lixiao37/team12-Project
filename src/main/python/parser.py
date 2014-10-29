from bs4 import BeautifulSoup
from article import *
from website import *
from user import *
import urllib2
import dryscrape

class Parser(object):
    """Generic Parser Class"""

    conn = None
    session = None
    host = "ds035260.mongolab.com:35260"
    dbName = "userinterface"
    base_url = "http://www.google.ca"
    search_meta = "/#q=%22{0}%22+site:{1}&tbas=0&tbs=qdr:{2},sbd:1"
    username = "admin"
    password = "admin"

    def __init__(self):
        self.session = dryscrape.Session(base_url=self.base_url)

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

    def searchArticle(self, q, site, since="y"):
        articles = []

        #How old data do we need to search for? E.g. qdr:y, means 
        #search articles upto one year old
        self.session.visit(self.search_meta.format(q, site, since))
        body = self.session.driver.body()
        soup = BeautifulSoup(body)
        for a in soup.find_all("a"):
                if a.parent.name == "h3":
                    articles.append(a)

        resultsPage = [a.get("href") for a in soup.find_all("a", "fl")]

        for page in resultsPage:
            self.session.visit(self.search_meta.format(q, site, since))
            body = self.session.driver.body()
            soup = BeautifulSoup(body)    
            for a in soup.find_all("a"):
                if a.parent.name == "h3":
                    articles.append(a)

        return list(set(articles))

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
    p = Parser()
    articles = p.searchArticle("pakistan", "www.aljazeera.com", since="d")
    for a in articles:
        print a.text
    print len(articles)

