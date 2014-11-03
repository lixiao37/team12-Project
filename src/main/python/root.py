import os, os.path
import cherrypy
from mako.template import Template
from mongoengine import *
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
    def modify_data(self, value=None, list_type=None, mod_type=None):
        user = User.objects(name=cherrypy.session["user"]).first()
        # checks to see if the textbox is empty
        if value == "":
            return "Fail: The text box is empty."
        if mod_type == "add":
            # adding news sources and targets
            if list_type == "#news_source":
                if value in user.news_sources:
                    return "Fail: This news link is already in the source list."
                else:
                    user.news_sources.append(value)
                    user.save()
            elif list_type == "#news_target":
                if value in user.news_targets:
                    return "Fail: This news link is already in the target list."
                else:
                    user.news_targets.append(value)
                    user.save()
            # adding twitter sources and targets
            elif list_type == "#twitter_source":
                if value in user.twitter_sources:
                    return "Fail: This twitter link is already in the source list."
                else:
                    user.twitter_sources.append(value)
                    user.save()
            elif list_type == "#twitter_target":
                if value in user.twitter_targets:
                    return "Fail: This twitter link is already in the target list."
                else:
                    user.twitter_targets.append(value)
                    user.save()
        elif mod_type == "delete":
            # deleting news sources and targets
            if list_type == "#news_source":
                if value in user.news_sources:
                    user.news_sources.remove(value)
                    user.save()
                else:
                    return "Fail: This news link is not in the source list"
            elif list_type == "#news_target":
                if value in user.news_targets:
                    user.news_targets.remove(value)
                    user.save()
                else:
                    return "Fail: This news link is not in the target list"
            # deleting twitter sources and targets
            elif list_type == "#twitter_source":
                if value in user.twitter_sources:
                    user.twitter_sources.remove(value)
                    user.save()
                else:
                    return "Fail: This twitter link is not in the source list"
            elif list_type == "#twitter_target":
                if value in user.twitter_targets:
                    user.twitter_targets.remove(value)
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

        return page_header + total_graphs
    
    # generate a detail bar graph from the relation_dict
    def generate_detailed_graph(self, relation_dict):
        user = User.objects(name=cherrypy.session["user"]).first()
        news_targets = user.news_targets
        news_targets_str = str(news_targets).replace("u'","'")
        graph_generator_template = Template(filename='detailed_graph_generator.html')
        return graph_generator_template.render(targets=news_targets_str, 
            sources=relation_dict.keys(), target_counts=relation_dict.values())

    # generate basic bar graphs from the relation_dict
    def generate_basic_graphs(self, relation_dict):
        user = User.objects(name=cherrypy.session["user"]).first()
        news_targets = user.news_targets
        total_basic_graphs = ""
        graph_generator_template = Template(filename='basic_graph_generator.html')
        for source, target_count in relation_dict.iteritems():
            news_targets_str = str(news_targets).replace("u'","'")
            total_basic_graphs += graph_generator_template.render(source=source, 
                targets=news_targets_str, target_count=target_count)
        return total_basic_graphs

    '''generates a list of string/string lists in the format
        [source, news_targets, target_count]
        ie. [[s1, [t1, t2 ... tn], [tc1, tc2, ... tcn]], 
        [s2, [t1, t2 ... tn], [tc1, tc2, ... tcn]], ...
        [sn, [t1, t2 ... tn], [tc1, tc2, ... tcn]]
        where sn is the source, tn is the target, tcn is the citation count of tn'''
    def generate_relation_dict(self):
        relation_dict = {}
        # get the current user's sources and targets
        user = User.objects(name=cherrypy.session["user"]).first()
        news_sources = user.news_sources
        news_targets = user.news_targets

        for source in news_sources:
            # create an empty list with a specific size which describe the number 
            # of target referenced by each source            
            target_count = [0] * len(news_targets)
            # Find the articles which have a specific source website url
            articles = Article.objects(website=Website.objects(homepage_url=source).first())
            for article in articles:
                # Count the times that each target in the news_targets is in the
                # citation list for each article and put it in the target_count
                for citation in article.citations:
                    if not isinstance( citation, int ):
                        if citation.target_article:
                            i = 0
                            while i < len(news_targets):
                                if citation.target_article.website.homepage_url == news_targets[i]:
                                    target_count[i] += 1
                                i += 1
            relation_dict[source] = target_count
        return relation_dict

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
    cherrypy.quickstart(Root(), '/', _cp_config)