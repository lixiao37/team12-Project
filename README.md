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
	- tweepy
	- warc

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

This will launch a webserver on your local computer. Then you can go to your internet browser and type "localhost:8080", this will take you to the report. Then, login using the username "guest", and leave the password blank. Then click on "Generate Graph", this will generate graphs from the live database.

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

### How to use the website
1. Install all the dependencies as mentioned above
2. Run by using 'python src/main/python/userinterface.py' in the project directory
3. Open a web browser and in the url go to localhost:8080
4. In the homepage, create a new account
5. Once created, login with your new account
6. Go to the Action Menu tab and go to Sources & Targets
7. Add the sources and targets for the News Section and Twitter Section, take note that 'http://' should not be included in the URL
8. Click the green bar at the top of the page to begin parsing, the parser will begin running so give it a few minutes to complete the task
9. Note that you can check on the progress of the parser in the Log tab
10. After the parsing is completed, go to the Action Menu and go to Articles. Here you can see a list of all the articles parsed and there is also an option to download it as warc
11. To render graphs for the news, go to the NewsGraph tab. Once there, click on at least one of the sources and targets and hit the Submit button to render the graph
12. To render graphs for the twitter, go to the TwitterGraph tab. Once there, click on at least one of the sources and targets and hit the Submit button to render the graph
13. To see the graphs, go to the Action Menu tab and go to Graphs. Once there, you can select which graph to view on the left side of the page
14. To extract the project files, go to the Action Menu tab and go to Git Hub Project Files. Once there, click on the GitHub link. Note that you will need access to that repository since it is private
