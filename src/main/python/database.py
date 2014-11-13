from mongoengine import *
from website import Website
from article import Article
from user import User
from citation import Citation


class Database(object):

    conn = None
    verbose = True
    host = "ds039020.mongolab.com:39020"
    dbName = "parser"
    username = "admin"
    password = "admin"

    def __init__(self, host=None, dbName=None, verbose=True):
        self.verbose = verbose
        if host:
            self.host = host
        if dbName:
            self.dbName = dbName

    def connect(self, username=None, password=None):
        '''Connect to the database'''

        if username and password:
            self.username = username
            self.password = password

        self.conn = connect(self.dbName, host=self.host, username=self.username,
                            password=self.password)
        if self.isConnect() and self.verbose:
            print "Connected to the \"{0}\" Database!".format(self.dbName)

    def isConnect(self):
        '''Check if connection exists with the database'''
        if self.conn:
            return True
        else:
            return False

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
            return None

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
            return None

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
                    article=citation_meta.get('article'),
                    target_name=citation_meta.get('target_name'),
                    target_article=citation_meta.get('target_article')
                ).first()

        if cite:
            print "Citation already exists!"
            return cite

        #This citation object is used to add to the database
        cite = Citation(
                    text=citation_meta.get('text'),
                    article=citation_meta.get('article'),
                    target_article=citation_meta.get('target_article'),
                    target_name=citation_meta.get('target_name')
                )
        status = cite.save()

        if status:
            article = citation_meta.get('article')
            article.citations.append(cite)
            article.save()
            return cite
        else:
            return None


