sudo apt-get install libqt4-dev libqtwebkit-dev qt4-qmake build-essential python-lxml python-pip
sudo apt-get install xvfb
git clone https://github.com/niklasb/dryscrape.git dryscrape
cd dryscrape
sudo pip install -r requirements.txt
sudo python setup.py install
cd ..
sudo rm -rf dryscrape
