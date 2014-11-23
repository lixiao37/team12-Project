import warc
from pywb.warc.recordloader import ArcWarcRecordLoader
from bs4 import BeautifulSoup
import requests
import re
import binascii

def WarcRecorder(message,url):
        #currently only allows creation on one file and one content in file
        #opens a new file for writing
        f = warc.open("test.warc.gz", "w")
        #creates Warc headers, warcinfo header is required, defaults=True generates missing fields
        #warc uses dictionary as internal structure
        header1 = warc.WARCHeader({"WARC-Type": "warcinfo", "WARC-Filename": "test.warc.gz"}, defaults=True)    
        header2 = warc.WARCHeader({"WARC-Type": "response", "WARC-Target-URI": url}, defaults=True)
        #creates the records for warc, first is header, second is the actual content
        record1 = warc.WARCRecord(header=header1, payload="software: warc\nformat: WARC Format 1.0\n", defaults=True) 
        record2 = warc.WARCRecord(header=header2, payload=message, defaults=True)
        #writes records to file, and close
        f.write_record(record1)
        f.write_record(record2)
        f.close()        

if __name__ == "__main__":
        #uses requests to scrape webpage, uses BeuatifulSoup as text
        url = "http://www.bbc.com/news/science-environment-30012854"
        r  = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data)
        string_soup = str(soup)
        WarcRecorder(string_soup, url)
    
        '''
        #opens a test.warc.gz file and prints its header data, uses pywb module
        #range 9000 chosen as test range and carries no other significances
        w = ArcWarcRecordLoader()
        for i in range(9000):
            try:
                v = w.load("test.warc.gz",i,9000)
                print v
                print i
            except:
                pass
        '''
        
        '''
        #opens test.warc.gz file and prints its header and contents, uses warc module
        t = warc.open("test.warc.gz")
        for h in t:
            print list(h.header)
            print list(h.payload)
        '''
        
        '''
        #warc file from https://ia601004.us.archive.org/4/items/Okmij00000.warc/
        y = ArcWarcRecordLoader()
        for i in range(9000):
                try:
                        v = y.load("example.warc.gz",i,9000)
                        print v
                        print i
                except:
                        pass  
        '''
        
        '''
        #warc file obtained from https://ia601004.us.archive.org/4/items/Okmij00000.warc/
        t = warc.open("okmij-00000.warc.gz")
        for h in t:
            print list(h.header)
            print list(h.payload)
        '''
        
        '''
        #warc file from https://github.com/ikreymer/pywb/tree/master/sample_archive/warcs
        y = ArcWarcRecordLoader()
        for i in range(9000):
                try:
                    v = y.load("example.warc.gz",i,9000)
                    print v
                    print i
                except:
                    pass  
        '''
        
        '''
        #warc file from https://github.com/ikreymer/pywb/tree/master/sample_archive/warcs
        t = warc.open("example.warc.gz")
        for h in t:
                print list(h.header)
                print list(h.payload)
        '''
        
'''
NOTES:
pywb only used for testing, not needed for warc creation

Tests
tests with pywb on test.warc.gz showed broken formating
while tests with other two .warc.gz shows correct formating

tests with warc on test.warc.gz showed correct formating
while tests with warc on other two .warc.gz shows incorrect characters

Possible Causes
formating of warc module may be incorrect when decoded by pywb
decoding by warc module may be faulty on non warc generated .warc.gz files
'''
