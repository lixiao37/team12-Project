# Team-12(CoffeeCoders):

### Dependencies:
	- pybuilder
	- cherrypy
	- mongoengine
	- beautifulsoup4
	- mako

Most of the dependencies are python modules, therefore you can install them
locally by running "pip install {module_name}".

We are using pybuilder, an automated python builder.
The source files are located under src/main/python/*.
The unittest files are located under src/unittest/python/*.

### How to build:
Run "pyb" in the root directory(where build.py exists).
This will build the entire project, and save the files into a separate folder,
called "target". Then you can look at the distribution files under,
**"target/dist/team12-Project1-1.0-SNAPSHOT"**

### Summary of source files:

###### user.py
	- This python file contains the schema for the User collection

###### article.py
	- This python file contains the schema for the Article collection. This collection
	will store all meta data associated with each articles.

###### citation.py
	- This python file contains the schema for the Citation collection. 
	
###### website.py
	- This python file contains the schema for the Website collection.

###### root.py
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

###### aljazeeraparser.py
	- This module is a child of the generic parser class, and it contains the
	parsing utilities specific to aljazeera website.

