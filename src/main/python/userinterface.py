import os, os.path
import cherrypy
import thread
import hashlib
import time
import logging
from mongoengine import *
from database import Database
from mako.template import Template
from mako.lookup import TemplateLookup
from parser import Parser
from twitterparser import TwitterParser
from user import User
from twitter import TwitterAccount
from twitter import Tweet
from article import Article
from website import Website
from citation import Citation
from authenticator import AuthController, require, member_of, name_is
    
mylookup = TemplateLookup(directories=['.'])
host = "ds053380.mongolab.com:53380"
dbName = "twitterparser"
username = "admin"
password = "admin"

#check for parser running
global parserRun, graph_thread_flag, graph_thread_running, user, logger
graph_thread_running = 0
graph_thread_flag = 1
parserRun = 0
username = None


class Root:
    auth = AuthController()
    relation_dict = {}
    twitter_relation_dict = {}

    @require() # requires user to be logged in to view page
    @cherrypy.expose
    def index(self): # index is our home page or root directory (ie. http://127.0.0.1:8080/)
        global graph_thread_running, username
        def graph_thread():
            global graph_thread_running, username
            global parserRun, graph_thread_flag
            global relation_dict, twitter_relation_dict
            logger.info('Started Thread on Relation Graphs')
            graph_thread_running = 1            
            runAgain = 1
            while graph_thread_flag:
                if parserRun == 1:
                    #wait for one minute for the parser to finish
                    logger.info('Pause Relation Dict')
                    runAgain = 1
                    while parserRun:
                        time.sleep(5)
                elif runAgain == 1:
                    logger.info('Running Relation Dict on {0}'.format(username))
                    #data has changed, generate the relation again
                    user = User.objects(name=username).first()
                    news_sources = user.news_sources
                    news_targets = user.news_targets
                    twitter_sources = user.twitter_sources
                    twitter_targets = user.twitter_targets
                    try:
                        relation_dict = self.generate_relation_dict(news_sources, news_targets)
                        twitter_relation_dict = self.generate_twitter_relation_dict(twitter_sources, twitter_targets)
                    except:
                        logger.info('Not Enough Data to Process For Graphs')
                    logger.info('Finish Updated Relation Dict')
                    runAgain = 0
                else:
                    time.sleep(5)
        
        if not graph_thread_running:
            thread.start_new_thread(graph_thread, ())
        username = cherrypy.session['user']
        index_page_template = Template(filename='index.html', lookup=mylookup)
        return index_page_template.render(username=cherrypy.session["user"], home="active")

    @cherrypy.expose
    def require_login(self): # This page is http://127.0.0.1:8080/require_login
        require_login_template = Template(filename='require_login.html', lookup=mylookup)
        return require_login_template.render(home="active")

    @cherrypy.expose
    def signup(self, username=None, password=None, from_page="/"):
        signup_template = Template(filename='signup.html')

        if username is None or password is None:
            return signup_template.render(msg="Enter login information", from_page=from_page)
        
        user_exist = self.check_user_exist(username)
        if user_exist:
            # username exist in the database, can't create
            return signup_template.render(msg="Username is taken, please try another one", from_page=from_page)
        else:
            # username does not exist in the database, can create it now
            group = "User"
            news_sources ={}
            news_targets ={}
            twitter_sources = []
            twitter_targets = []

            p = hashlib.md5()
            p.update(password)
            User(name = username,
                password = p.hexdigest(),
                group = group,
                news_sources = news_sources,
                news_targets = news_targets,
                twitter_sources = twitter_sources,
                twitter_targets = twitter_targets).save()

            # go to home page
            raise cherrypy.HTTPRedirect(from_page or "/")

    def check_user_exist(self, username):
        # See if the username is in the database, also if the password is correct
        if User.objects(name=username):
            return True
        else:
            return False

    @require() # requires user to be logged in to view page
    @cherrypy.expose
    def about(self):
        about_template = Template(filename='about.html', lookup=mylookup)
        return about_template.render(username=cherrypy.session["user"], about="active")

    @require() # requires user to be logged in to view page
    @cherrypy.expose
    def git_hub_project(self):
        git_project_template = Template(filename='git_hub_project.html', lookup=mylookup)
        return git_project_template.render(username=cherrypy.session["user"])

    @require() # requires user to be logged in to view page
    @cherrypy.expose
    def log(self):
        log_template = Template(filename='log.html', lookup=mylookup)
        try:
            logContent = open('beta.log').readlines()
        except IOError:
            logContent = []
        if len(logContent) > 50:
            logContent = logContent[ len(logContent) - 50: ]
        logContent = reversed(logContent)
        return log_template.render(logContent=logContent, username=cherrypy.session["user"], log="active")

    @cherrypy.expose
    def modify_data(self, value_name=None, 
        list_type=None, mod_type=None, value_url=None):
        user = User.objects(name=cherrypy.session["user"]).first()
        # checks to see if the textbox is empty
        if value_name == "":
            return "Fail: The name text box is empty."
        if mod_type == "add":
            # adding news sources and targets
            if list_type == "#news_source_name":
                if value_url == "":
                    return "Fail: The url text box is empty."                
                if value_name in user.news_sources.keys() \
                or value_url in user.news_sources.values():
                    return "Fail: This news name or link is already in the source list."
                else:
                    user.news_sources[value_name] = value_url
                    user.save()
            elif list_type == "#news_target_name":
                if value_url == "":
                    return "Fail: The url text box is empty."                
                if value_name in user.news_targets.keys() \
                or value_url in user.news_targets.values():
                    return "Fail: This news name or link is already in the target list."
                else:
                    user.news_targets[value_name] = value_url
                    user.save()
            # adding twitter sources and targets
            elif list_type == "#twitter_source_name":
                if value_name in user.twitter_sources:
                    return "Fail: This twitter screen name is already in the source list."
                else:
                    user.twitter_sources.append(value_name)
                    user.save()
            elif list_type == "#twitter_target_name":
                if value_name in user.twitter_targets:
                    return "Fail: This twitter screen name is already in the target list."
                else:
                    user.twitter_targets.append(value_name)
                    user.save()
        elif mod_type == "delete":
            # deleting news sources and targets
            if list_type == "#news_source_name":
                if value_url == "":
                    return "Fail: The url text box is empty."                
                if value_name in user.news_sources.keys() \
                and value_url in user.news_sources.values():
                    del user.news_sources[value_name]
                    user.save()
                else:
                    return "Fail: This news link is not in the source list"
            elif list_type == "#news_target_name":
                if value_url == "":
                    return "Fail: The url text box is empty."                
                if value_name in user.news_targets.keys() \
                and value_url in user.news_targets.values():
                    del user.news_targets[value_name]
                    user.save()
                else:
                    return "Fail: This news link is not in the target list"
            # deleting twitter sources and targets
            elif list_type == "#twitter_source_name":
                if value_name in user.twitter_sources:
                    user.twitter_sources.remove(value_name)
                    user.save()
                else:
                    return "Fail: This twitter screen name is not in the source list"
            elif list_type == "#twitter_target_name":
                if value_name in user.twitter_targets:
                    user.twitter_targets.remove(value_name)
                    user.save()
                else:
                    return "Fail: This twitter screen name is not in the target list"
        return "Success!"

    # gets the user's list accordingly and returns it to the tracking page
    @require() # requires user to be logged in to view page
    @cherrypy.expose
    def get_list(self, list_type = None):
        user = User.objects(name=cherrypy.session["user"]).first()
        show_list_template = Template(filename='show_list.html')
        show_twitter_list_template = Template(filename='show_twitter_list.html')
        if 'news_source_list' == list_type:
            list_name = user.news_sources
            return show_list_template.render(list_name=list_name)
        elif 'news_target_list' == list_type:
            list_name = user.news_targets
            return show_list_template.render(list_name=list_name)
        elif 'twitter_source_list' == list_type:
            list_name = user.twitter_sources
            return show_twitter_list_template.render(list_name=list_name)
        elif 'twitter_target_list' == list_type:
            list_name = user.twitter_targets
            return show_twitter_list_template.render(list_name=list_name)

    @require() # requires user to be logged in to view page
    @cherrypy.expose
    def tracking_list(self): # This page is http://127.0.0.1:8080/tracking_list
        track_template = Template(filename='track.html', lookup=mylookup)
        return track_template.render(username=cherrypy.session["user"])
    
    @cherrypy.expose
    def get_articles(self):
        show_article_template = Template(filename='get_articles.html')
        articles = Article.objects()
        return show_article_template.render(articles=articles)
    
    @require() # requires user to be logged in to view page
    @cherrypy.expose
    def display_articles(self):
        article_template = Template(filename='display_articles.html', lookup=mylookup)
        return article_template.render(username=cherrypy.session["user"])
    
    @require() # requires user to be logged in to view page
    @cherrypy.expose
    def display_graphs_overview(self):
        # generate a relation list, described in more depth at the fnc
        # self.relation_dict = self.generate_relation_dict()
        # self.twitter_relation_dict = self.generate_twitter_relation_dict()

        global relation_dict, twitter_relation_dict
        generate_template = Template(filename='generate_graphs_overview.html', lookup=mylookup)
        try:
            self.relation_dict = relation_dict
            self.twitter_relation_dict = twitter_relation_dict
            available = True
        except NameError:
            available = False
        return generate_template.render(username=cherrypy.session["user"], available=available)

    @require() # requires user to be logged in to view page
    @cherrypy.expose
    def display_news_bar(self):
        # self.relation_dict = self.generate_relation_dict()
        global relation_dict
        self.relation_dict = relation_dict
        graphs = self.generate_detailed_graph(self.relation_dict, "news")

        generate_template = Template(filename='display_graphs.html', lookup=mylookup)
        return generate_template.render(username=cherrypy.session["user"], 
            graphs=graphs, section_name="News", graph_type="Bar")

    @require() # requires user to be logged in to view page
    @cherrypy.expose
    def display_news_pie(self):
        # self.relation_dict = self.generate_relation_dict()
        global relation_dict
        self.relation_dict = relation_dict
        graphs = self.generate_completed_pie_graphs(self.relation_dict, "news")

        generate_template = Template(filename='display_graphs.html', lookup=mylookup)
        return generate_template.render(username=cherrypy.session["user"], 
            graphs=graphs, section_name="News", graph_type="Pie")

    @require() # requires user to be logged in to view page
    @cherrypy.expose
    def display_twitter_bar(self):
        # self.twitter_relation_dict = self.generate_twitter_relation_dict()
        global twitter_relation_dict
        self.twitter_relation_dict = twitter_relation_dict
        graphs = self.generate_detailed_graph(self.twitter_relation_dict, "twitter")

        generate_template = Template(filename='display_graphs.html', lookup=mylookup)
        return generate_template.render(username=cherrypy.session["user"], 
            graphs=graphs, section_name="Twitter", graph_type="Bar")

    @require() # requires user to be logged in to view page
    @cherrypy.expose
    def display_twitter_pie(self):
        # self.twitter_relation_dict = self.generate_twitter_relation_dict()
        global twitter_relation_dict
        self.twitter_relation_dict = twitter_relation_dict
        graphs = self.generate_completed_pie_graphs(self.twitter_relation_dict, "twitter")

        generate_template = Template(filename='display_graphs.html', lookup=mylookup)
        return generate_template.render(username=cherrypy.session["user"], 
            graphs=graphs, section_name="Twitter", graph_type="Pie")

    @require() # requires user to be logged in to view page
    @cherrypy.expose
    def generate_graphs_overview(self):
        page_header = ""
        total_graphs = ""

        # get the page header section
        graph_generator_template = Template(filename='graph_page_header.html')
        page_header += graph_generator_template.render(name=cherrypy.session["user"])

        # generate a relation list, described in more depth at the fnc
        relation_dict = self.generate_relation_dict()
        twitter_relation_dict = self.generate_twitter_relation_dict()

        if relation_dict:
            # generate basic bar graphs and add them to total_graphs
            total_graphs += self.generate_basic_graphs(relation_dict)

            # generate a combined news detailed graph and add it to total_graphs
            total_graphs += self.generate_detailed_graph(relation_dict, "news")
            
            # generate pie graphs and add it to total_graphs
            total_graphs += self.generate_completed_pie_graphs(relation_dict, "news")
        
        if twitter_relation_dict:
            # generate a combined twitter detailed graph and add it to total_graphs
            total_graphs += self.generate_detailed_graph(twitter_relation_dict, "twitter")
            
            # generate pie graphs and add it to total_graphs
            total_graphs += self.generate_completed_pie_graphs(twitter_relation_dict, "twitter")

        return page_header + total_graphs 
    
    def generate_pie_graph(self, relation_dict, index, target):
        # generate the whole graph dataset
        sources_counts = []
        data = ""
        for source in relation_dict:
            data+= '{value : ' + str(relation_dict.get(source)[index]) + ',color : randomColor(),label: "' + source + '"},'
            sources_counts.append(relation_dict.get(source)[index])
        data = data[0:-1]
        # generate the pie graph only if at aleast one count in sources_counts
        # is not 0
        for count in sources_counts:
            if count != 0:
                graph_generator_template = Template(filename='pie_generator.html')
                return graph_generator_template.render(target=target, data=data,
                    sources_counts=sources_counts)
        return "<h1>Pie Graph for target " + target + "</h1><br/>Sorry, we can't generate this pie, since the source count is " + str(sources_counts) + " for this target.<br>"
    
    def generate_completed_pie_graphs(self, relation_dict, datatype):
        user = User.objects(name=cherrypy.session["user"]).first()
        if datatype == "news":
            sources = user.news_sources.keys()
            targets = user.news_targets.values()
        elif datatype == "twitter":
            sources = user.twitter_sources
            targets = user.twitter_targets
        pie_graphs = ""
        i = 0
        # generate the pie graph only if traking more than two sources and more
        # than one targets
        if len(sources) >= 2 and targets:
            for target in targets:
                pie_graphs += self.generate_pie_graph(relation_dict, i, target)
                i += 1
        return pie_graphs
    
    # generate a detail bar graph from the relation_dict
    def generate_detailed_graph(self, relation_dict, datatype):
        user = User.objects(name=cherrypy.session["user"]).first()
        if datatype == "news":
            targets = user.news_targets.values()
        elif datatype == "twitter":
            targets = user.twitter_targets
        targets_str = str(targets).replace("u'","'")
        total_bar = len(relation_dict.keys()) * len(targets_str.split(","))
        # generate the whole graph dataset
        data = ""
        if relation_dict:
            for source in relation_dict:
                data+= '{fillColor : randomColor(),strokeColor : "rgba(151,187,205,0.8)",data: ' + str(relation_dict.get(source)) + ',label: "' + source + '"},'
            data = data[0:-1]
            graph_generator_template = Template(filename='detailed_graph_generator.html')
            return graph_generator_template.render(targets=targets_str,
                    sources=relation_dict.keys(), target_counts=relation_dict.values(),
                    value_space=600/(6+total_bar), dataset_space=((600/(6+total_bar))/5),
                    data=data, datatype=datatype)
        else:
            return ""

    # generate basic bar graphs from the relation_dict
    def generate_basic_graphs(self, relation_dict):
        user = User.objects(name=cherrypy.session["user"]).first()
        news_targets = user.news_targets.values()
        total_basic_graphs = ""
        graph_generator_template = Template(filename='basic_graph_generator.html')
        for source, target_count in relation_dict.iteritems():
            news_targets_str = str(news_targets).replace("u'","'")
            total_basic_graphs += graph_generator_template.render(source=source, 
                targets=news_targets_str, target_count=target_count)
        return total_basic_graphs

    def generate_twitter_relation_dict(self, twitter_sources, twitter_targets):
        relation_dict = {}
        # user = User.objects(name=cherrypy.session["user"]).only('twitter_sources', 'twitter_targets').first()
        # twitter_sources = user.twitter_sources
        # twitter_targets = user.twitter_targets
        
        for twitter_sources_screenname in twitter_sources:
            target_count = [0] * len(twitter_targets)
            i = 0
            for twitter_target in twitter_targets:
                target_count[i] = TwitterParser(data=data).count_ref(twitter_sources_screenname, twitter_target)
                i += 1
            relation_dict[twitter_sources_screenname] = target_count
        return relation_dict
                    

    '''generates a dictionary of string/list(int) in the format
        {source : target_count}
        ie. {s1 : [tc1, tc2, ... tcn], 
        s2 : [tc1, tc2, ... tcn], ...
        sn : [tc1, tc2, ... tcn]}
        where sn is the source, tcn is the citation count of each target'''
    def generate_relation_dict(self, news_sources, news_targets):
        relation_dict = {}
        # get the current user's sources and targets
        # user = User.objects(name=cherrypy.session["user"]).only('news_sources', 'news_targets').first()
        # news_sources = user.news_sources
        # news_targets = user.news_targets

        for source_name, source_url in news_sources.iteritems():
            # create an empty list with a specific size which describe the number 
            # of target referenced by each source            
            target_count = [0] * len(news_targets)
            # Find the articles which have a specific source website url
            articles = Article.objects(
                Q(website=Website.objects(homepage_url=source_url).only('homepage_url').first()) & 
                Q(citations__exists=True)).only('citations')
            for article in articles:
                # Count the times that each target in the news_targets is in the
                # citation list for each article and put it in the target_count
                for citation in article.citations:
                    if not isinstance( citation, int ):
                        i = 0
                        while i < len(news_targets):
                            if citation.target_name.lower() == news_targets.keys()[i].lower():
                                target_count[i] += 1
                            i += 1
            relation_dict[source_name] = target_count
        return relation_dict
    
    @require() # requires user to be logged in to view page
    @cherrypy.expose
    def parse(self):
        
        global parserRun
        if parserRun == 1:
            return "Fail: Parser is already running"

        def threaded_parser(p, t_p, sources, targets, twitter_sources, twitter_targets, logger):
            logger.info("Started Parser Background")
            global parserRun
            parserRun = 1

            #TwitterParser For Sources
            try:
                t_p.run(twitter_sources)
            except Exception, e:
                logger.error('Twiiter Parser(Sources) Failed', exc_info=True)
            #TwitterParser For Targets
            try:
                t_p.run(twitter_targets)
            except Exception, e:
                logger.error('Twiiter Parser(Targets) Failed', exc_info=True)
            #News Website Parser
            try:
                p.run(sources, targets)
            except Exception, e:
                logger.error('News Parser Failed', exc_info=True)                      
            parserRun = 0

        user = User.objects(name=cherrypy.session["user"]).first()
        sources = user.news_sources
        targets = user.news_targets
        twitter_sources = user.twitter_sources
        twitter_targets = user.twitter_targets

        p = Parser(data=data, logger=logger) 
        
        t_p = TwitterParser(data=data, logger=logger)
        t_p.authorize()      
        
        thread.start_new_thread( threaded_parser , 
                        (p, t_p, sources, targets, twitter_sources, twitter_targets, p.logger))

        logger.info('Executing Parser Commands')
        return "Success: Parser Running In The Background"

    @require()
    @cherrypy.expose
    def isParserRunning(self):
        global parserRun
        if parserRun:
            return "Yes"
        else:
            return "No"

if __name__ == '__main__':
    global logger
    #create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    # create a file handler
    handler = logging.FileHandler('beta.log')
    handler.setLevel(logging.INFO)
    # create a logging format
    formatter = logging.Formatter(\
                     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(handler)
    
    data = Database(host=host, dbName=dbName)
    data.connect(username=username, password=username)

    _cp_config = {
        '/': {
            'tools.sessions.on': True,
            'tools.auth.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8080,})
    cherrypy.quickstart(Root(), '/', _cp_config)
