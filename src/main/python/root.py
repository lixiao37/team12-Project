import cherrypy
from mako.template import Template
from mongoengine import *
from user import User
from article import Article
from authenticator import AuthController, require, member_of, name_is

connect("userinterface", host="ds035260.mongolab.com:35260", username="admin", password="admin")

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

    _cp_config = {
        'tools.sessions.on': True,
        'tools.auth.on': True
    }

    auth = AuthController()

    restricted = RestrictedArea()

    @cherrypy.expose
    @require() # requires logged in status to view page
    def index(self): # index is our home page or root directory (ie. http://127.0.0.1:8080/)
        return '''<html><body bgcolor="pink"><center>
                    <h1 style="color:#0033CC">Welcome to Menu!</h1>
                    <input type="button" value="Tracking sources and targets" onclick="location='/tracking_list'">
                    <br/>
                    <input type="button" value="Display articles" onclick="location='/display'">
                    <br/>
                    <input type="button" value="Generate Graph" onclick="location='/generate_graph'">
                    <br/>
                    <br/>
                    <form method="post" action="/auth/logout">
                    <input type="submit" value="Log out" />
                    </form>
                </center></body></html>''' % locals()

    @cherrypy.expose
    def home(self): # This page is http://127.0.0.1:8080/home
        return """<html><body bgcolor="pink"><center>
            <h1 style="color:#0033CC">Welcome to the Home Page!</h1>
            <input type="button" value="Log in" 
            style="height:50px; width:100px" onClick="location='/auth/login'"/>
            <br>
            <br>
            To continue and use the system, you must login to your account.
        </center></body></html>""" % locals()
    
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
        return track_template.render()
    
    @cherrypy.expose
    def display_show_articles(self):
        show_article_template = Template(filename='show_articles.html')
        articles = Article.objects()
        return show_article_template.render(articles=articles)
    
    @require()
    @cherrypy.expose
    def display(self): # This page is http://127.0.0.1:8080/display
        article_template = Template(filename='articles.html')
        return article_template.render()
    
    @require()
    @cherrypy.expose
    def generate_graph(self): # This page is http://127.0.0.1:8080/generate_graph
        graph_template = Template(filename='graph.html')
        return graph_template.render()

    # @require()
    # @cherrypy.expose
    # def get_graphs(self):
    #     #total_graphs = ''
    #     # for loop over sources to get website
    #         # count how many citations there are for each target for that source
    #         # total_graphs += show_graphs_template.render(source=source, targets=targets, target_count=targetcount)
    #     show_graphs_template = Template(filename='show_graphs.html')
    #     return show_graphs_template.render(source=source, targets=targets, target_count=targetcount)

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
    cherrypy.quickstart(Root())