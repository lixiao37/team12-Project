import cherrypy
from authenticator import AuthController, require, member_of, name_is

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
        return """"<html><body bgcolor="pink"><center>
                    <h1 style="color:#0033CC">Logout Screen</h1>
                    <form method="post" action="/auth/logout">
                    <input type="submit" value="Log out" />
                </center></body></html>""" % locals()
    
    @cherrypy.expose
    def home(self): # This page is http://127.0.0.1:8080/home
        return """<html><body bgcolor="pink"><center>
        <h5> This page is open to everyone including people who hasn't logged in</h5>
            <h1 style="color:#0033CC">Main Screen</h1>
            I want to log in the system!
            <input type="button" value="Log in" onClick="location='/auth/login'"/>
        </center></body></html>""" % locals()
    
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
