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

def get_meta_data(url):
	'''
	Return all the meta info of the given article url,
	E.g. {"author": "Ali Mehdi", "url": "", title: ""}
	'''
	pass

if __name__ == '__main__':
	p = Parser()
	print p.url_list("dad")