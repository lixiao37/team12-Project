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
        #return """<center><h1 style="color:#0033CC">Home Screen</h1>
        #This page only requires a valid login.</center>"""
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
    def track_sources(self):
        sources = User.Objects().sources
        return """% for a in sources:
                <li>a</li>
                % endfor"""
    
    @cherrypy.expose
    def track_targets(self):
        targets = User.Objects().targets
        return """% for a in targets:
                <li>a</li>
                % endfor"""        

    @cherrypy.expose
    def tracking_list(self): # This page is http://127.0.0.1:8080/tracking_list
        track_template = Template(filename='track.html')
        return track_template.render()
    
    @cherrypy.expose
    def display_show_articles(self):
        show_article_template = Template(filename='show articles.html')
        articles = Article.objects()
        return show_article_template.render(articles=articles)

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
