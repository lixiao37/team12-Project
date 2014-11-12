from bs4 import BeautifulSoup
from article import *
from website import *
from user import *
from citation import *
from requests.exceptions import ConnectionError
import requests
import re
import dryscrape
import tempfile
import sys

class Parser(object):
    '''Generic Parser Class'''

    conn = None
    session = None
    verbose = True
    host = "ds039020.mongolab.com:39020"
    dbName = "parser"
    #base_url = ""
    google_url = "http://www.google.ca"
    
    #{0}:keyword, {1}:website, {2}:sort by month or year or day
    search_meta = "http://www.google.ca/#q=%22{0}%22+site:{1}&tbas=0&tbs=qdr:{2},sbd:1"
    username = "admin"
    password = "admin"
    
    #different names for author's meta data
    date_names = ["LastModifiedDate", "lastmod", "OriginalPublicationDate", 'datePublished']
    title_names = ['Headline', 'title', 'og:title']

    def __init__(self, host=None, dbName=None, verbose=True):
        '''Initialize a session to connect to the database'''
        self.session = dryscrape.Session()
        self.verbose = verbose
        if host and dbName:
            self.connect(host=host, dbName=dbName)
        else:
            self.connect(host=self.host, dbName=self.dbName)

    def connect(self, host=None, dbName=None):
        '''Connect to the database'''
        self.conn = connect(dbName, host=host, username=self.username,
                        password=self.password)
        if self.isConnect():
            if self.verbose:
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

    def add_article(self, article_meta, website):
        '''Add the article in the database'''
        
        #Create an article object to check if it exists in the database
        art = Article.objects(
                    title=article_meta.get("title"),
                    url=article_meta.get('url'),
                    last_modified_date=article_meta.get('last_modified_date'),
                    website=website
                    ).first()
        
        if art:
            if self.verbose:
                print "Article already exists and has not been updated"
            return art
        
        #This article object is used to add to the database
        art = Article(
                title=article_meta.get("title"),
                author=article_meta.get("author"),
                last_modified_date=article_meta.get("last_modified_date"),
                html=article_meta.get("html"),
                url=article_meta.get("url"),
                website=website
                    )
        status = art.save()
        
        if status:
            return art
        else:
            return 0

    def add_website(self, website_meta):
        '''Add the website in the database'''
        
        #Create a website object to check if it exists in the database
        web = Website.objects(
                    name=website_meta.get("name"),
                    homepage_url=website_meta.get("homepage_url")
                ).first()
        
        if web:
            return web
        
        #This website object is used to add to the database
        web = Website(
                name=website_meta.get("name"),
                homepage_url=website_meta.get("homepage_url")
                )
        status = web.save()
        
        if status:
            return web
        else:
            return 0

    def add_citation(self, citation_meta):
        '''
        Add the citation in the database. There are 3 types of citations:
        1. The target name exists in the text
        2. The target name exists as a link to the target url in the text
        3. The target name does not exist in the text but a different name that 
        links to the target url is in the text
        '''
        
        #Create a citation object to check if it exists in the database
        cite = Citation.objects(
                    text=citation_meta.get('text'),
                    article=citation_meta.get('article')
                ).first()
        
        if cite:
            return 0
        
        #This citation object is used to add to the database
        cite = Citation(
                    text=citation_meta.get('text'),
                    article=citation_meta.get('article'),
                    target_article=citation_meta.get('target_article'),
                    target_name=citation_meta.get('target_name')
                )
        status = cite.save()
        
        if status:
            return cite
        else:
            return 0

    def extract_citation(self, soup, target_url, target_name, article):
        '''
        Return a list of citations, where
        soup: html
        target_url: url of the target, e.g. bbc.com
        target_name: name of the target, e.g. Haaretz
        '''
        cited = {}
        text = ""
        website = self.add_website( \
                               {"name": target_name, "homepage_url": target_url}
                                    )
        
        #Compile a list of urls that contains the given target url
        key_href_list = soup.find_all(href=re.compile(target_url))
        for a in key_href_list:
            #Loop through the parent html code in the url
            for parent in a.parents:
                #If the parent html code contains the specified code, create a
                #citation object and store it in database and the article
                if parent.name == 'p' or parent.name == 'div' \
                                                       or parent.name == 'span':
                        article_meta = self.get_meta_data(a.get('href').strip())
                        target_article = self.add_article(article_meta, website)
                        cite = self.add_citation({"text":parent.text,
                                           "article": article,
                                           "target_article": target_article,
                                           "target_name": target_name})
                        article.citations.append(cite)
                        article.save()
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
                        cite = self.add_citation({"text":parent.text,
                                           "article": article,
                                           "target_name": target_name})
                        break

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
            if anchor_name in self.title_names or Property in self.title_names:
                content = m.get('content').encode('utf-8')
                meta['title'] = content
            if anchor_name in self.date_names or item_prop in self.date_names:
                content = m.get('content').encode('utf-8')
                meta['last_modified_date'] = content
            if 'author' == anchor_name:
                content = m.get('content').encode('utf-8')
                meta['author'] = content

        if not meta.get('title'):
            meta['title'] = ''

        return meta

    def get_screenshot_binary(self, url):
        '''
        Takes a screenshot of the article and return a binary representation 
        of it.
        '''

        # visit the url
        self.session.visit(url)

        # define a temporary jpg file to be read as binary
        temp = tempfile.NamedTemporaryFile(mode='rb', suffix = '.jpg')

        # save the temporary file of the web page 
        self.session.render(temp.name)

        binary = temp.read()
        
        # temporary file is removed
        temp.close()
        return binary


if __name__ == '__main__':
    #p = Parser()
    #print p.get_screenshot_binary('http://www.aljazeera.com/')

    #Both the sources and targets are dictionaries and the format is
    #{ source/target name: source/target url }
    sources = { "Al Jazeera": "www.aljazeera.com", "BBC": "www.bbc.com",
                    'CNN': 'www.cnn.com' }
    targets = { "Haaretz": "www.haaretz.com" }
    p = Parser()
    
    for s_name, s in sources.viewitems():
        website = p.add_website({"name": s_name, "homepage_url": s})
        for t_name, t in targets.viewitems():
            articles = p.searchArticle(t_name, s)
            for a in articles:
                article_meta = p.get_meta_data(a)
                article = p.add_article(article_meta, website)
                p.extract_citation(article_meta.get('html'), t, t_name, article)

