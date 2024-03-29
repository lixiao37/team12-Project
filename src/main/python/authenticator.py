# Open source module: Authentication system 
# from http://tools.cherrypy.org/wiki/AuthenticationAndAccessRestrictions
# Source Author: Arnar Birgisson
# Customized by Chun and Zhen

import cherrypy
import hashlib
from cgi import escape
from mongoengine import *
from user import User

SESSION_KEY = '_cp_username'

# Might be userful for later - Chun
# def createUserInDB(username, password):
#     p = hashlib.md5()
#     p.update('coffeecoders')
    
#     newUser = User(name=username)
#     newUser.password = p.hexdigest()
#     newUser.save()

def check_credentials(username, password):
    """Verifies username and password.
    Returns None on success or a string describing the error on failure"""
    # Converts the password to hash md5
    p = hashlib.md5()
    p.update(password)

    # See if the username is in the database, also if the password is correct
    if User.objects(Q(name=username) & Q(password=p.hexdigest())):
        return None
    else:
        return u"Username or password is incorrect or not found in database."

def check_auth(*args, **kwargs):
    """A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as a list of
    conditions that the user must fulfill"""
    conditions = cherrypy.request.config.get('auth.require', None)
    if conditions is not None:
        username = cherrypy.session.get(SESSION_KEY)
        if username:
            cherrypy.request.login = username
            for condition in conditions:
                # A condition is just a callable that returns true or false
                if not condition():
                    # If the user is logged in but does not fufill the conditions, bring them to login
                    raise cherrypy.HTTPRedirect("/auth/login")
        else:
            # If the user has is not logged in, brings them to the login page for the first time
            raise cherrypy.HTTPRedirect("/require_login")
    
cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)

def require(*conditions):
    """A decorator that appends conditions to the auth.require config
    variable."""
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate


# Conditions are callables that return True
# if the user fulfills the conditions they define, False otherwise
# To tell who the currently logged in username, refer to cherrypy.request.login

def member_of(groupname):
    def check():
        # need to add database part - chun
        # replace with database check if <username> is in <groupname>
        return cherrypy.request.login == 'chun' and groupname == 'admin'
    return check

def name_is(reqd_username):
    return lambda: reqd_username == cherrypy.request.login

# These might be handy
# Conditions are callables that return True
def any_of(*conditions):
    """Returns True if any of the conditions match"""
    def check():
        for c in conditions:
            if c():
                return True
        return False
    return check

# By default all conditions are required, but this might still be
# needed if you want to use it inside of an any_of(...) condition
def all_of(*conditions):
    """Returns True if all of the conditions match"""
    def check():
        for c in conditions:
            if not c():
                return False
        return True
    return check


# Controller to provide login and logout actions

class AuthController(object):
    
    def on_login(self, username):
        """Called on successful login"""
        cherrypy.session["user"] = username
    
    def on_logout(self, username):
        """Called on logout"""
        cherrypy.session.pop("user", None)
    
    def get_loginform(self, username, msg="Enter login information", from_page="/"):
        # 2 lines of code to prevent XSS vulnerability
        username = escape(username, True)
        from_page = escape(from_page, True)
        return """
                <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <title>Project: Relation Parser</title>

                        <!-- Bootstrap core CSS -->
                        <link href="/static/css/bootstrap.min.css" rel="stylesheet">

                        <!-- Custom styles for this template -->
                        <link href="/static/css/login.css" rel="stylesheet">
                    </head>

                    <body>
                        <div class="container">
                            <form class="form-signin" role="form" method="post" action="/auth/login">
                                <h2 class="form-signin-heading">
                                    Login Screen </br>
                                    <small><input type="hidden" name="from_page" 
                                        value="%(from_page)s"/>%(msg)s<br/></small></h2>
                                        
                                <label for="username" class="sr-only">Username</label>
                                <input type="text" name="username" class="form-control" 
                                    value="%(username)s" placeholder="Username" required autofocus>

                                <label for="password" class="sr-only">Password</label>
                                <input type="password" name="password" class="form-control" placeholder="Password">
                                
                                <div class="checkbox">
                                  <label>
                                    <input type="checkbox" value="remember-me"> Remember me
                                  </label>
                                </div>
                                
                                <button class="btn btn-lg btn-primary btn-block" type="submit">Sign in</button>
                            </form>
                        </div>


                    </body>
                </html>""" % locals()

    @cherrypy.expose
    def login(self, username=None, password=None, from_page="/"):
        if username is None or password is None:
            return self.get_loginform("", from_page=from_page)
        
        error_msg = check_credentials(username, password)
        if error_msg:
            return self.get_loginform(username, error_msg, from_page)
        else:
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
            self.on_login(username)
            raise cherrypy.HTTPRedirect(from_page or "/")
    
    @cherrypy.expose
    def logout(self, from_page="/"):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None
            self.on_logout(username)
        raise cherrypy.HTTPRedirect(from_page or "/")
