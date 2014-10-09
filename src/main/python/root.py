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
    @require()
    def index(self):
        return """<center><h1 style="color:#0033CC">Home Screen</h1>
        This page only requires a valid login.</center>"""
    
    @cherrypy.expose
    def open(self):
        return """This page is open to everyone including people who hasn't logged in"""
    
    @cherrypy.expose
    @require(name_is("chun"))
    def only_for_chun(self):
        return """Hello Chun - this page is available to you only"""

    # This is only available if the user name is chun and he's in group admin
    @cherrypy.expose
    @require(name_is("chun"))
    @require(member_of("admin"))
    def only_for_chun_admin(self):
        return """Hello Chun, the Admin - this page is available to you only and because you are admin"""


if __name__ == '__main__':
    cherrypy.quickstart(Root())