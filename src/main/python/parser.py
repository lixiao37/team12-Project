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
    """Generic Parser Class"""

    conn = None
    session = None
    host = "ds039020.mongolab.com:39020"
    dbName = "parser"
    base_url = "http://www.google.ca"
    search_meta = "/#q=%22{0}%22+site:{1}&tbas=0&tbs=qdr:{2},sbd:1"
        #{0}:keyword, {1}:website, {2}:sort by month or year or day
    username = "admin"
    password = "admin"
    #different names for author's meta data
    date_names = ["LastModifiedDate", "lastmod", "OriginalPublicationDate", 'datePublished']
    title_names = ['Headline', 'title', 'og:title']

    def __init__(self):
        self.session = dryscrape.Session(base_url=self.base_url)

        #Connect to the database
        self.connect()

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

    def add_article(self, article_meta, website):
        #check if the article is already in the database
        art = Article.objects(
                    title=article_meta.get("title"),
                    url=article_meta.get('url'),
                    last_modified_date=article_meta.get('last_modified_date'),
                    website=website
                    ).first()
        if art:
            print "Article already exists and has not been updated"
            return art
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
        web = Website.objects(
                    name=website_meta.get("name"),
                    homepage_url=website_meta.get("homepage_url")
                ).first()
        #check if the website is already in the database
        if web:
            return web
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
        cite = Citation.objects(
                    text=citation_meta.get('text'),
                    article=citation_meta.get('article')
                ).first()
        if cite:
            return 0
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
        Return the list of citations, where
        soup: html
        target_url: url of the target, e.g. bbc.com
        target_name: name of the target, e.g. Haaretz
        '''
        cited = {}
        text = ""
        website = self.add_website( \
                               {"name": target_name, "homepage_url": target_url}
                                    )
        key_href_list = soup.find_all(href=re.compile(target_url))
        for a in key_href_list:
            for parent in a.parents:
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

        key_text_list = soup.find_all(text=re.compile(target_name))
        for t in key_text_list:
            for parent in t.parents:
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
        Return all the meta info of the given article url,
        E.g.
        {author: "", "url": "", title: "", last_modified_date: "", html: ""}
        '''
        try:
            r = requests.get(url, timeout=60) #send http request
        except ConnectionError:
            return self.get_meta_data(url)
        content = r.content #get the content
        soup = BeautifulSoup(content) #put it into beautifulsoup
        meta = {}
        meta['html'] = soup
        meta['url'] = r.url

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
        Takes a screenshot of the article and return a binary representation of it.
        '''
        self.base_url = url

        # set up a web scraping session
        self.session = dryscrape.Session(base_url = self.base_url)

        # visit homepage and search for a term
        self.session.visit('/')

        temp = tempfile.NamedTemporaryFile(mode='rb', suffix = '.jpg')

        # save a screenshot of the web page
        self.session.render(temp.name)

        binary = temp.read()
        temp.close()
        return binary


if __name__ == '__main__':
    #p = Parser()
    #print p.get_screenshot_binary('http://www.aljazeera.com/')

    sources = { "Al Jazeera": "www.aljazeera.com", "BBC": "www.bbc.com",
                    'CNN': 'www.cnn.com'}
    targets = { "Haaretz":"www.haaretz.com" }
    # sources = {'CNN': 'www.cnn.com'}
    # targets = {'BBC':'www.bbc.com'}
    p = Parser()
    for s_name, s in sources.viewitems():
        website = p.add_website({"name": s_name, "homepage_url": s})
        for t_name, t in targets.viewitems():
            articles = p.searchArticle(t_name, s)
            for a in articles:
                article_meta = p.get_meta_data(a)
                article = p.add_article(article_meta, website)
                p.extract_citation(article_meta.get('html'), t, t_name, article)


