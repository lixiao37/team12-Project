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
                    <h1 style="color:#0033CC">Welcome to menu!</h1>
                    <input type="button" value="Tracking sources and targets" onclick="location='/tracking_list'">
                    <input type="button" value="Display articles" onclick="location='/display'">
                    <br/>
                    <form method="post" action="/auth/logout">
                    <br/>
                    <input type="submit" value="Log out" />
                    </form>
                </center></body></html>''' % locals()

    @cherrypy.expose
    def home(self): # This page is http://127.0.0.1:8080/home
        return """<html><body bgcolor="pink"><center>
        <h5> This page is open to everyone including people who hasn't logged in</h5>
            <h1 style="color:#0033CC">Main Screen</h1>
            I want to log in the system!
            <input type="button" value="Log in" onClick="location='/auth/login'"/>
        </center></body></html>""" % locals()
    
    @cherrypy.expose
    def modify_data(self, value=None, list_type=None, mod_type=None):
        user = User.objects(name=cherrypy.session["user"]).first()
        # checks to see if the textbox is empty
        if value == "":
            return "Fail: The text box is empty."
        if mod_type == "add":
            if list_type == "#sources":
                if value in user.sources:
                    return "Fail: This website is already in the source list."
                else:
                    user.sources.append(value)
                    user.save()
            elif list_type == "#targets":
                if value in user.targets:
                    return "Fail: This website is already in the target list."
                else:
                    user.targets.append(value)
                    user.save()
        elif mod_type == "delete":
            if list_type == "#sources":
                if value in user.sources:
                    user.sources.remove(value)
                    user.save()
                else:
                    return "Fail: This website is not in the source list"
            elif list_type == "#targets":
                if value in user.targets:
                    user.targets.remove(value)
                    user.save()
                else:
                    return "Fail: This website is not in the target list"
        return "Success!"              
    
    # gets the user's list of sources and returns it to the tracking page    
    @cherrypy.expose
    def track_sources(self):
        user = User.objects(name=cherrypy.session["user"]).first()
        show_sources_template = Template(filename='show_sources.html')
        sources = user.sources
        return show_sources_template.render(sources=sources)
    
    # gets the user's list of targets and returns it to the tracking page
    @cherrypy.expose
    def track_targets(self):
        user = User.objects(name=cherrypy.session["user"]).first()
        show_targets_template = Template(filename='show_targets.html')
        targets = user.targets
        return show_targets_template.render(targets=targets)
    
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