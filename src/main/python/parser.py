from bs4 import BeautifulSoup
import urllib2

class Parser(object):
	"""Generic Parser Class"""

	def __init__(self):
		pass
	
	def url_list(self, search):
		url = 'http://www.aljazeera.com/Services/Search/?q=' + search
		content = urllib2.urlopen(url).read()
		soup = BeautifulSoup(content)
		list_of_url = []
	     
		for anchor in soup.find_all('a'):
			#print anchor
			print(anchor.get('href'))
			list_of_url.append(anchor.get('href'))
			
		return list_of_url	
        
def get_author_name(url):
	'''
	Return the author's name from the given url,
	if author does not exist, then return empty string.
	'''
	pass

def get_article_title(url):
	'''
	Return the article's title from the given url,
	if title does not exist, then return empty string.
	'''
	pass

if __name__ == '__main__':
	p = Parser()
	print p.url_list("dad")