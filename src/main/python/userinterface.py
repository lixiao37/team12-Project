import os, os.path
import cherrypy
import thread
from mako.template import Template
from mongoengine import *
from parser import *
from user import User
from article import Article
from website import Website
from citation import Citation
from authenticator import AuthController, require, member_of, name_is

connect("parser", host="ds039020.mongolab.com:39020", username="admin", password="admin")

class RestrictedArea:

    # all methods in this controller (and subcontrollers) is
    # open only to members of the admin group

    _cp_config = {
        'auth.require': [member_of('admin')]
    }

    @cherrypy.expose
    def index(self):
        return """This area requires admin group status."""


class Root:
    auth = AuthController()

    restricted = RestrictedArea()

    @cherrypy.expose
    @require() # requires logged in status to view page
    def index(self): # index is our home page or root directory (ie. http://127.0.0.1:8080/)
        index_page_template = Template(filename='index.html')
        return index_page_template.render(name=cherrypy.session["user"])
        
    @cherrypy.expose
    def home(self): # This page is http://127.0.0.1:8080/home
        home_page_template = Template(filename='home.html')
        return home_page_template.render()
    
    @cherrypy.expose
    def example(self):
        return """ hi"""

    @cherrypy.expose
    def modify_data(self, value_name=None, 
        value_url=None, list_type=None, mod_type=None):
        user = User.objects(name=cherrypy.session["user"]).first()
        # checks to see if the textbox is empty
        if value_url == "" or value_name == "":
            return "Fail: The name or url text box is empty."
        if mod_type == "add":
            # adding news sources and targets
            if list_type == "#news_source_name":
                if value_name in user.news_sources.keys() \
                or value_url in user.news_sources.values():
                    return "Fail: This news name or link is already in the source list."
                else:
                    user.news_sources[value_name] = value_url
                    user.save()
            elif list_type == "#news_target_name":
                if value_name in user.news_targets.keys() \
                or value_url in user.news_targets.values():
                    return "Fail: This news name or link is already in the target list."
                else:
                    user.news_targets[value_name] = value_url
                    user.save()
            # adding twitter sources and targets
            elif list_type == "#twitter_source_name":
                if value_name in user.twitter_sources.keys() \
                or value_url in user.twitter_sources.values():
                    return "Fail: This twitter name or link is already in the source list."
                else:
                    user.twitter_sources[value_name] = value_url
                    user.save()
            elif list_type == "#twitter_target_name":
                if value_name in user.twitter_targets.keys() \
                or value_url in user.twitter_targets.values():
                    return "Fail: This twitter name or link is already in the target list."
                else:
                    user.twitter_targets[value_name] = value_url
                    user.save()
        elif mod_type == "delete":
            # deleting news sources and targets
            if list_type == "#news_source_name":
                if value_name in user.news_sources.keys() \
                and value_url in user.news_sources.values():
                    del user.news_sources[value_name]
                    user.save()
                else:
                    return "Fail: This news link is not in the source list"
            elif list_type == "#news_target_name":
                if value_name in user.news_targets.keys() \
                and value_url in user.news_targets.values():
                    del user.news_targets[value_name]
                    user.save()
                else:
                    return "Fail: This news link is not in the target list"
            # deleting twitter sources and targets
            elif list_type == "#twitter_source_name":
                if value_name in user.twitter_sources.keys() \
                and value_url in user.twitter_sources.values():
                    del user.twitter_sources[value_name]
                    user.save()
                else:
                    return "Fail: This twitter link is not in the source list"
            elif list_type == "#twitter_target_name":
                if value_name in user.twitter_targets.keys() \
                and value_url in user.twitter_targets.values():
                    del user.twitter_targets[value_name]
                    user.save()
                else:
                    return "Fail: This twitter link is not in the target list"
        return "Success!"

    # gets the user's list accordingly and returns it to the tracking page    
    @cherrypy.expose
    def get_list(self, list_type = None):
        user = User.objects(name=cherrypy.session["user"]).first()
        show_list_template = Template(filename='show_list.html')
        if 'news_source_list' == list_type:
            list_name = user.news_sources
        elif 'news_target_list' == list_type:
            list_name = user.news_targets
        elif 'twitter_source_list' == list_type:
            list_name = user.twitter_sources
        elif 'twitter_target_list' == list_type:
            list_name = user.twitter_targets
        return show_list_template.render(list_name=list_name)

    @require()
    @cherrypy.expose
    def tracking_list(self): # This page is http://127.0.0.1:8080/tracking_list
        track_template = Template(filename='track.html')
        return track_template.render(name=cherrypy.session["user"])
    
    @cherrypy.expose
    def display_show_articles(self):
        show_article_template = Template(filename='show_articles.html')
        articles = Article.objects()
        return show_article_template.render(articles=articles)
    
    @require()
    @cherrypy.expose
    def display(self): # This page is http://127.0.0.1:8080/display
        article_template = Template(filename='articles.html')
        return article_template.render(name=cherrypy.session["user"])
    
    @require()
    @cherrypy.expose
    def generate_graphs(self):
        page_header = ""
        total_graphs = ""

        # get the page header section
        graph_generator_template = Template(filename='graph_page_header.html')
        page_header += graph_generator_template.render(name=cherrypy.session["user"])

        # generate a relation list, described in more depth at the fnc
        relation_dict = self.generate_relation_dict()

        # generate basic bar graphs and add them to total_graphs
        total_graphs += self.generate_basic_graphs(relation_dict)

        # generate a combined detailed graph and add it to total_graphs
        total_graphs += self.generate_detailed_graph(relation_dict)
        
        # generate pie graphs and add it to total_graphs
        total_graphs += self.generate_completed_pie_graphs(relation_dict)

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
    
    def generate_completed_pie_graphs(self, relation_dict):
        user = User.objects(name=cherrypy.session["user"]).first()
        news_sources = user.news_sources
        news_targets = user.news_targets.values()
        pie_graphs = ""
        i = 0
        # generate the pie graph only if traking more than two sources and more
        # than one targets
        if len(news_sources) >= 2 and news_targets:
            for target in news_targets:
                pie_graphs += self.generate_pie_graph(relation_dict, i, target)
                i += 1
        return pie_graphs

    # generate a detail bar graph from the relation_dict
    def generate_detailed_graph(self, relation_dict):
        user = User.objects(name=cherrypy.session["user"]).first()
        news_targets = user.news_targets.values()
        news_targets_str = str(news_targets).replace("u'","'")
        total_bar = len(relation_dict.keys()) * len(news_targets_str.split(","))
        # generate the whole graph dataset
        data = ""
        for source in relation_dict:
            data+= '{fillColor : randomColor(),strokeColor : "rgba(151,187,205,0.8)",data: ' + str(relation_dict.get(source)) + ',label: "' + source + '"},'
        data = data[0:-1]
        graph_generator_template = Template(filename='detailed_graph_generator.html')
        return graph_generator_template.render(targets=news_targets_str,
                sources=relation_dict.keys(), target_counts=relation_dict.values(),
                value_space=600/(6+total_bar), dataset_space=((600/(6+total_bar))/5),
                data=data)

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

    def generate_twitter_relation_dict(self):
        relation_dict = {}
        user = User.objects(name=cherrypy.session["user"]).only('twitter_sources', 'twitter_targets').first()

    '''generates a list of string/string lists in the format
        [source, news_targets, target_count]
        ie. [[s1, [t1, t2 ... tn], [tc1, tc2, ... tcn]], 
        [s2, [t1, t2 ... tn], [tc1, tc2, ... tcn]], ...
        [sn, [t1, t2 ... tn], [tc1, tc2, ... tcn]]
        where sn is the source, tn is the target, tcn is the citation count of tn'''
    def generate_relation_dict(self):
        relation_dict = {}
        # get the current user's sources and targets
        user = User.objects(name=cherrypy.session["user"]).only('news_sources', 'news_targets').first()
        news_sources = user.news_sources
        news_targets = user.news_targets

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
    
    @require()
    @cherrypy.expose
    def parse(self):
        
        def threaded_parser(p, sources, targets):
            p.run(sources, targets)

        host = "ds053380.mongolab.com:53380"
        dbName = "twitterparser"
        user = User.objects(name=cherrypy.session["user"]).first()
        sources = user.news_sources
        targets = user.news_targets
        p = Parser(host=host, dbName=dbName)        
        thread.start_new_thread( threaded_parser , (p, sources, targets))

        return "Success"        
        
    @cherrypy.expose
    @require(name_is("chun")) # requires the logged in user to be chun
    def only_for_chun(self):
        return """Hello Chun - this page is available to you only"""

    # This is only available if the user name is chun and he's in group admin
    @cherrypy.expose
    @require(name_is("chun")) # requires the logged in user to be chun
    @require(member_of("admin")) # requires the logged in user to be a member of the admin group
    def only_for_chun_admin(self):
        return """Hello Chun, the Admin - this page is available to you only and because you are admin"""


if __name__ == '__main__':
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
    cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': 8080,
                       })
    cherrypy.quickstart(Root(), '/', _cp_config)
