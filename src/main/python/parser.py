from bs4 import BeautifulSoup
from article import *
from website import *
from user import *
from citation import *
from requests.exceptions import ConnectionError
import requests
import re
import urllib2
import dryscrape

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
    date_names = ["LastModifiedDate", "lastmod", "OriginalPublicationDate"]
    title_names = ['Headline', 'title', 'title']

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

    def extract_citation(self, soup, target_url, target_name):
        '''
        Return the list of citations, where
        soup: html
        target_url: url of the target, e.g. bbc.com
        target_name: name of the target, e.g. Haaretz
        '''
        cited = []
        text = ""
        key_href_list = soup.find_all(href=re.compile(target_url))
        for a in key_href_list:
            for parent in a.parents:
                if parent.name == 'p' or parent.name == 'div' \
                                                       or parent.name == 'span':
                        cited.append(parent)
                        break

        key_text_list = soup.find_all(text=re.compile(target_name))
        for t in key_text_list:
            for parent in t.parents:
                    if parent.name == 'p' or parent.name == 'div' \
                            or parent.name == 'span' or parent.name == 'h1' \
                                or parent.name == 'h2' or parent.name == 'h3':
                        cited.append(parent.text)
                        break
            # if t.parent.name == 'strong':
            #     if t.parent.parent.name == 'em':
            #         cited.append(t.parent.parent)
            #     else:
            #         cited.append(t.parent.parent)
            # elif t.parent.name == 'em' or t.parent.name == 'a':
            #     if t.parent.parent.name == 'p':
            #         cited.append(t.parent.parent)
            #     else:
            #         cited.append(t.parent.parent.parent)
            # else:
            #     if t.parent not in cited:
            #         cited.append(t.parent)

        return list(set(cited))

    def get_meta_data(self, url):
        '''
        Return all the meta info of the given article url,
        E.g.
        {author: "", "url": "", title: "", last_modified_date: "", html: ""}
        '''
        try:
            r = requests.get(url, timeout=60) #send http request
        except ConnectionError:
            #try again
            return self.get_meta_data(url)
            # r = requests.get(url, timeout=60) #send http request
        content = r.content #get the content
        soup = BeautifulSoup(content) #put it into beautifulsoup

        meta = {}
        meta['html'] = soup
        meta['url'] = r.url

        for anchor in soup.find_all('meta'):
            anchor_name = anchor.get('name')
            if anchor_name in self.title_names:
                #get the title of the article
                content = anchor.get('content').encode('utf-8')
                meta['title'] = content
            if anchor_name in self.date_names:
                content = anchor.get('content').encode('utf-8')
                meta['last_modified_date'] = content
            if 'author' == anchor_name:
                content = anchor.get('content').encode('utf-8')
                meta['author'] = content

        return meta

    def add_to_database(self, article_meta=None, website_meta=None,
                        citation_meta=None):
        '''API function to add parsed data into the database'''
        citations = []

        web = Website.objects(
                    name=website_meta.get("name"),
                    homepage_url=website_meta.get("homepage_url")
                    ).first()
        #check if the website is already in the database
        if not web:
            web = Website(
                    name=website_meta.get("name"),
                    homepage_url=website_meta.get("homepage_url")
                    ).save()

        #check if the article is already in the database
        art = Article.objects(
                    title=article_meta.get("title"),
                    url=article_meta.get('url'),
                    last_modified_date=article_meta.get('last_modified_date'),
                    website=web
                    ).first()
        if art:
            print "Article already exists and has not been updated"
            print article_meta.get("url")
            return 0

        art = Article(
                title=article_meta.get("title"),
                author=article_meta.get("author"),
                last_modified_date=article_meta.get("last_modified_date"),
                html=article_meta.get("html"),
                url=article_meta.get("url"),
                website=web
                    )

        status = art.save()
        if status:
            for c in citation_meta:
                cit = Citation(text=c.encode('utf-8'),  article=art,    target_article=art)
                citations.append(cit)
                cit.save()

            art.citations = citations
            art.save()
            return 0
        else:
            print "ERROR: Article did not save successfully ...!"
            return 0


if __name__ == '__main__':
    sources = { "Al Jazeera": "www.aljazeera.com", "BBC": "www.bbc.com",
                    'CNN': 'www.cnn.com'}
    targets = { "Haaretz":"www.haaretz.com" }
    # sources = {'CNN': 'www.cnn.com'}
    # targets = {'BBC':'www.bbc.com'}
    p = Parser()
    for s_name, s in sources.viewitems():
        for t_name, t in targets.viewitems():
            articles = p.searchArticle(t_name, s)
            for a in articles:
                article_data = p.get_meta_data(a)

                web_data = { "name":s_name, "homepage_url":s }
                cited_data = p.extract_citation(
                                            article_data.get('html'), t, t_name)
                p.add_to_database(
                    article_meta=article_data,
                    website_meta=web_data,
                    citation_meta=cited_data
                    )
