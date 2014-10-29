from bs4 import BeautifulSoup
import requests

url = "http://www.aljazeera.com/indepth/features/2014/10/end-hong-kong-dream-201410592243801352.html"
target = 'globalpropertyguide'

r  = requests.get(url)
data = r.text
soup = BeautifulSoup(data)

for link in soup.find_all('p'):
    if target in str(link):
        print(link.get_text())
        for inlink in link.find_all('a'):
            if target in str(inlink):
                extern = inlink.get('href')
print(extern)
