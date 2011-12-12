import cherrypy

class ThermotypGUI(object):
    def index(self):
        return "Hi World!"
    index.exposed = True

cherrypy.quickstart(ThermotypGUI())
