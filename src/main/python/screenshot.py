import dryscrape
import gzip
import binascii
import os

class Screenshot(object):
    """Generic Screenshot class"""

    def __init__(self):
        self
        
    def convert_to_binary(self, base_url): 
        self.base_url = base_url
        
        # set up a web scraping session
        self.sess = dryscrape.Session(base_url = self.base_url)           
           
        # visit homepage and search for a term
        self.sess.visit('/')
        
        # save a screenshot of the web page
        self.sess.render('picture.jpg')
        
        f_read = open('picture.jpg', 'rb')
        f_write = gzip.open('picture.gz', 'wb')
        f_write.writelines(f_read)
        f_write.close()
        f_read.close()
        os.remove('picture.jpg')
        f_read_zip = open('picture.gz', 'rb')
        with f_read_zip:
            byte = f_read_zip.read(1)
            hexadecimal = binascii.hexlify(byte)
            decimal = int(hexadecimal, 16)
            binary = bin(decimal)[2:].zfill(8)
        f_read_zip.close()
        os.remove('picture.gz')
        return binary      
        
if __name__ == '__main__':
    screen = Screenshot()
    print screen.convert_to_binary('http://www.aljazeera.com/')