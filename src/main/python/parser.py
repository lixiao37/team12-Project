from bs4 import BeautifulSoup
from article import *
from website import *
from user import *
from citation import *
from requests.exceptions import ConnectionError
from database import Database
import logging
import requests
import re
import dryscrape
import tempfile
import sys

class Parser(object):
    '''
    News Website Parser that parses the news articles.
    '''

    conn = None
    session = None
    host = "ds039020.mongolab.com:39020"
    dbName = "parser"
    data = None
    google_url = "http://www.google.ca"
    log = 'beta.log'
    logger = None
    #{0}:keyword, {1}:website, {2}:sort by month or year or day
    search_meta = \
          "http://www.google.ca/#q=%22{0}%22+site:{1}&tbas=0&tbs=qdr:{2},sbd:1"
    username = "admin"
    password = "admin"

    #different names for author's meta data
    date_names = ["LastModifiedDate", "lastmod", "OriginalPublicationDate", 
                                                                'datePublished']
    title_names = ['Headline', 'title', 'og:title']

    def __init__(self, log=None, data=None, logger=logger):
        '''Initialize a session to connect to the database'''
        if log:
            self.log = log
        if not data:
            raise Exception("No Database Connection Found")
        if logger:
            self.logger = logger
        self.data = data        

        self.session = dryscrape.Session()

    def searchArticle(self, q, site, since="y"):
        '''
        Search for a keyword on Google and return the list of urls.
        q=keyword, site=website_url, since=sort_by_last_modified
        '''
        articles = []
        m = re.compile(".*"+site+".*")

        #Search articles based on when it was released. E.g. qdr:y, means
        #search articles upto a year old
        self.session.visit(self.search_meta.format(q, site, since))
        body = self.session.driver.body()
        soup = BeautifulSoup(body)

        for a in soup.find_all("a"):
                if a.parent.name == "h3":
                    url = a.get("href")
                    complete_url = self.google_url + url
                    if not m.match(complete_url):
                        continue
                    articles.append(complete_url)

        resultsPage = [a.get("href") for a in soup.find_all("a", "fl")]

        for page in resultsPage:
            self.session.visit(self.google_url + page)
            body = self.session.driver.body()
            soup = BeautifulSoup(body)
            for a in soup.find_all("a"):
                if a.parent.name == "h3":
                    url = a.get("href")
                    complete_url = self.google_url + url
                    if not m.match(complete_url):
                        continue
                    articles.append(complete_url)

        return list(set(articles))

    def get_citation(self, soup, target_url, target_name):
        '''
        Return a dictionary of citations extracted from the given html,
        and using the parameters, target_url and target_name
        '''
        cited = {}
        numCited = 0
        #Compile a list of urls that contains the given target url
        key_href_list = soup.find_all(href=re.compile(target_url))
        for a in key_href_list:
            #Loop through the parent html code in the url
            for parent in a.parents:
                #If the parent html code contains the specified code, create a
                #citation object and store it in database and the article
                if parent.name == 'p' or parent.name == 'div' \
                                                       or parent.name == 'span':
                    cited[numCited] = {"text": parent.text,
                                       "href": a.get('href').strip()}
                    numCited += 1
                    break

        #Compile a list of texts that contains the given target name
        key_text_list = soup.find_all(text=re.compile(target_name))
        for t in key_text_list:
            #Loop through the parent html code in the text
            for parent in t.parents:
                #If the parent html code contains the specified code, create a
                #citation object and store it in the database
                if parent.name == 'p' or parent.name == 'div' \
                        or parent.name == 'span' or parent.name == 'h1' \
                            or parent.name == 'h2' or parent.name == 'h3' \
                                or parent.name == 'h4':
                    cited[numCited] = {"text": parent.text, "href": ""}
                    numCited += 1
                    break

        return cited

    def add_citations(self, cited, target_url, target_name, article):
        '''Some Docstring'''
        website = self.data.add_website(
                              {"name": target_name, "homepage_url": target_url})

        for i in cited:
            each_citation = cited[i]
            if each_citation["href"]:
                article_meta = self.get_meta_data(each_citation["href"])
                target_article = self.data.add_article(article_meta, website)
                cite = self.data.add_citation(
                    {"text": each_citation["text"],
                     "article": article,
                     "target_article": target_article,
                     "target_name": target_name})
            else:
                cite = self.data.add_citation(
                    {"text": each_citation["text"],
                     "article": article,
                     "target_name": target_name})

    def get_meta_data(self, url):
        '''
        Return all the meta info of the given article url.
        E.g.
        {author: "", "url": "", title: "", last_modified_date: "", html: ""}
        '''
        try:
            #send http request
            r = requests.get(url, timeout=60)
        except ConnectionError:
            return self.get_meta_data(url)

        #get the content of the url
        content = r.content

        #put the content into beautifulsoup
        soup = BeautifulSoup(content)
        meta = {}
        meta['html'] = soup
        meta['url'] = r.url

        #Check all the meta in the url source and add the title, last modified
        #date and the author of the article into the meta dictionary
        for m in soup.find_all('meta'):
            anchor_name = m.get('name')
            Property = m.get('property')
            item_prop = m.get('itemprop')
            if anchor_name in self.title_names:
                content = m.get('content').encode('utf-8')
                meta['title'] = content
            if anchor_name in self.date_names or item_prop in self.date_names:
                content = m.get('content').encode('utf-8')
                meta['last_modified_date'] = content
            if 'author' == anchor_name:
                content = m.get('content').encode('utf-8')
                meta['author'] = content

        #Special case to find the title of the target website
        if not meta.get('title') and soup.find(itemprop="headline"):
            meta['title'] = soup.find(itemprop="headline")\
                                                   .text.encode("utf-8").strip()

        #special case for haaretz
        if not meta.get('title') and soup.find('hgroup'):
            hgroup = soup.find("hgroup")
            if hgroup.find('h1'):
                meta["title"] = hgroup.find('h1').text

        #special case for ynetnews
        if not meta.get('title') and soup.find('h1') and soup.find('h1', class_='text20b'):
            meta['title'] = soup.find('h1', class_='text20b').text

        #last resort, if cant find the title
        if not meta.get('title') and soup.find('title'):
            meta['title'] = soup.find('title').text

        #finall leave it blank
        if not meta.get('title'):
            meta['title'] = ''

        #Special case to find the author of the target website
        if not meta.get('author'):
            #This case is for human author
            if soup.find(rel="author"):
                meta['author'] = soup.find(rel="author")\
                                                   .text.encode("utf-8").strip()
            # This case if for non-human author (i.e. organization, another web 
            # site source)
            elif soup.find(itemprop="author"):
                hold = soup.find(itemprop="author").findChildren()
                if hold:
                    meta['author'] = hold[len(hold)-1]\
                                                   .text.encode("utf-8").strip()

        if not meta.get('author'):
            meta["author"] = ""

        return meta

    def run(self, sources, targets):
        '''Run the website parser using the parameters'''
        if self.logger:
            self.logger.info('Started Website Parsing')
        for s_name, s in sources.viewitems():
            website = self.data.add_website({"name": s_name, "homepage_url": s})
            for t_name, t in targets.viewitems():
                articles = self.searchArticle(t_name, s)
                for a in articles:
                    article_meta = self.get_meta_data(a)
                    article = self.data.add_article(article_meta, website)
                    if not article:
                        continue
                    citations = self.get_citation(
                                            article_meta.get('html'), t, t_name)
                    self.add_citations(citations, t, t_name, article)
        if self.logger:
            self.logger.info("Done Parsing Websites")
        return True


if __name__ == '__main__':
    pass
    # host = "ds053380.mongolab.com:53380"
    # dbName = "twitterparser"
    # data = Database(host=host, dbName=dbName)
    # data.connect()
    # # sources = { "Al Jazeera": "www.aljazeera.com", "BBC": "www.bbc.com",
    #                 # 'CNN': 'www.cnn.com' }
    # # targets = { "Haaretz": "www.haaretz.com", "Ahram":"www.english.ahram.org.eg"}

    # sources = {'Globe and Mail' : 'www.theglobeandmail.com'}
    # targets = {'Haaretz' : 'www.haaretz.com'}  
    
    # url = "http://www.ynetnews.com/articles/0,7340,L-4595629,00.html"

    # parse = Parser(data=data)
    # print parse.get_meta_data(url)["title"]
    # # parse.run(sources, targets)



