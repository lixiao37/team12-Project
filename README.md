# Team-12(CoffeeCoders):

### Branches
	- master (stable, for releases)
	- develop (unstable, for development)

**Note to TA: Please checkout the master branch for the latest/final release.**

### Dependencies:
	- pybuilder
	- cherrypy
	- mongoengine
	- beautifulsoup4
	- mako
	- dryscrape

Most of the dependencies are python modules, therefore you can install them
locally by running "pip install {module_name}".

However, there is a textfile that lists all the dependencies required. And you can run "pip install -r requirements.txt", this will install all the required python dependencies.

#### Installing Dependencies:
Run the following commands:

	- $ sudo pip install -r requirements.txt
	- $ sudo sh dryscrape.sh
The first script will install all python dependencies. 
And the second script will install **dryscrape**, which is a python module for HTTP requests.

***Note: The dryscrape module uses X11, if the build fails with the error "Cant Connect To X11", then you should run the build using the following command:***

	- $ xvfb-run pyb
***"xvfb"*** is an alternate to X11. You can install this easily using sudo apt-get install command.

### How to build:
This project uses an automated python builder, called pybuilder.

The source files are located under src/main/python/*.
The unittest files are located under src/unittest/python/*.

Run **"pyb"** in the root directory(where build.py exists).
This will build the entire project, and save the build files into a separate folder,
called "target". The python builder will also run the unittests, which are located in src/main/python/*.

The build files will be located under:
**"target/dist/team12-Project1-1.0-SNAPSHOT"**

### Looking at the report
After the build is done, please go to **"target/dist/team12-Project1-1.0-SNAPSHOT"** and write.

	- $ python userinterface.py

This will launch a webserver on your local computer. Then you can go to your internet browser and type "localhost:8080", this will take you to the report.

The data that you will see is live data from a database, located at mongolab.com
Note: You have to login using the username "guest" and leave the password blank.

### Critical source files:

###### user.py
	- This python file contains the schema for the User collection

###### article.py
	- This python file contains the schema for the Article collection. This collection
	will store all meta data associated with each articles.

###### citation.py
	- This python file contains the schema for the Citation collection. 
	
###### website.py
	- This python file contains the schema for the Website collection.

###### userinterface.py
	- This file contains the User Interface for our system.
    It works together with the authenticator.py, parser and the searcher
    to generate pages for the user to see.

###### authenticator.py
	- This file controls user login and logout. When the user
	tries to log in with their credentials in the User Interface, the
	authenticator checks to see if the acocunt exist in the database, also
	the password matches correctly.

###### parser.py
	- This module is a generic class for all parsers. It contains methods like
	"add to database", and "connect to the database" etc.
