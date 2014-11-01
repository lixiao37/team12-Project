from bs4 import BeautifulSoup
from article import *
from website import *
from user import *
import re
import urllib2
import dryscrape

class Parser(object):
    """Generic Parser Class"""

    conn = None
    session = None
    host = "ds035260.mongolab.com:35260"
    dbName = "userinterface"
    base_url = "http://www.google.ca"
    #{0}:keyword, {1}:website, {2}:sort by month or year or day
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
        '''
        Search for a keyword on Google and return the list of urls.
        q=keyword, site=website_url, since=sort_by_last_modified
        '''
        articles = []
        m = re.compile(".*"+site+".*")

        #How old data do we need to search for? E.g. qdr:y, means
        #search articles upto one year old
        self.session.visit(self.search_meta.format(q, site, since))
        body = self.session.driver.body()
        soup = BeautifulSoup(body)
        for a in soup.find_all("a"):
                if a.parent.name == "h3":
                    url = a.get("href")
                    complete_url = self.base_url + url
                    if not m.match(complete_url):
                        continue
                    articles.append(complete_url)

        resultsPage = [a.get("href") for a in soup.find_all("a", "fl")]

        for page in resultsPage:
            self.session.visit(page)
            body = self.session.driver.body()
            soup = BeautifulSoup(body)
            for a in soup.find_all("a"):
                if a.parent.name == "h3":
                    url = a.get("href")
                    complete_url = self.base_url + url
                    if not m.match(complete_url):
                        continue
                    articles.append(complete_url)

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
    articles = p.searchArticle("haaretz", "www.bbc.com")
    for a in articles:
        print a
    print len(articles)

