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
			print anchor.get('href')
			list_of_url.append(anchor.get('href'))

		return list_of_url

	def get_meta_data(self, url):
		'''
		Return all the meta info of the given article url,
		E.g. {"author": "Ali Mehdi", "url": "", title: ""}
		'''
		content = urllib2.urlopen(url).read()
		soup = BeautifulSoup(content)	
		dictionary = {}
		
		for anchor in soup.find_all('meta'):
			if 'title' in str(anchor):
				dictionary['Title'] = str(anchor.get('content').strip())
			
		for anchor in soup.find_all('meta'):
			if 'author' in str(anchor):
				dictionary['Author'] = str(anchor.get('content').strip())
				
		for anchor in soup.find_all('meta'):
			if 'LastModifiedDate' in str(anchor):
				dictionary['Date Modified'] = str(anchor.get('content'))
				
		dictionary['html'] = soup
				
		for anchor in soup.find_all('link'):
			if 'canonical' in str(anchor):
				dictionary['url'] = str(anchor.get('href'))
				
		return dictionary

if __name__ == '__main__':
	p = Parser()
	print p.get_meta_data('http://www.aljazeera.com/news/europe/2014/10/british-mps-back-recognition-palestine-20141013214237623951.html')