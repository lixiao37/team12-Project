import dryscrape
from bs4 import BeautifulSoup
from parser import *

class AlJazeeraParser(Parser):

    session = None
    base_url = "http://www.aljazeera.com"
    search_url = "/Services/Search/?q={}&r={}"
    name = "AlJazeera"
    country = "Qatar"
    db_website_object = None

    def __init__ (self):
        #create a connection to the website
        self.session = dryscrape.Session(base_url=self.base_url)

        #connect to the database
        if not self.isConnect():
            self.connect()

        #add website meta data into the database
        web = Website.objects(
                    name=self.name,
                    homepage_url=self.base_url,
                    country=self.country
                    ).first()
        if not web:
            web = Website(
                    name=self.name,
                    homepage_url=self.base_url,
                    country=self.country
                    )
            status = web.save()
        self.db_website_object = web

    def search(self, q, limit=100):
        '''
        Search in aljazeera website for the keyword articles, and return the
        list of urls of all the resulted articles.
        '''

        self.session.visit(self.search_url.format(q, limit))
        body = self.session.driver.body()
        soup = BeautifulSoup(body)

        #get all the div's that contain the search list
        all_articles = soup.find_all("div", "indexText-Bold2")
        return [article.a['href'] for article in all_articles]

    def get_meta_data(self, url):
        '''
        Return all the meta info of the given article url,
        E.g.
        {author: "", "url": "", title: "", last_modified_date: "", html: ""}
        '''
        content = urllib2.urlopen(url).read()
        soup = BeautifulSoup(content)

        dictionary = {}
        dictionary['html'] = soup
        dictionary['url'] = url

        for anchor in soup.find_all('meta'):
            if 'title' in str(anchor):
                dictionary['title'] = str(anchor.get('content').strip())

            if 'author' in str(anchor):
                dictionary['author'] = str(anchor.get('content').strip())

            if 'LastModifiedDate' in str(anchor):
                dictionary['last_modified_date'] = str(anchor.get('content'))

        return dictionary

if __name__ == '__main__':
    p = AlJazeeraParser()
    all_list = p.search('haaretz', limit=15)
    for a in all_list:
        meta = p.get_meta_data(a)
        p.add_to_database(meta)
