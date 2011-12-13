import cherrypy
import webbrowser
import json
from jinja2 import Template

class TTProgram(object):
    name =''
    modules = []
    template = """
<div class="programheader" id="programname">{{name}}</div>
<div class="programbody">
{% for m in modules %}
  {% set moduleindex = loop.index %}
  <div class="moduleheader">
    <a class="modify" href="/modify_program?removemodule={{moduleindex}}">[X]</a>
    <div class="edit" id="modulename_{{moduleindex}}">{{m.name}}</div>
    <a class="modify" href="/modify_program?addmodule={{moduleindex}}">[+]</a>
  </div>
  <div class="modulebody">
    {% for s in m.segments %}
      {% set segment_index = loop.index %}
      <div class="edit" id="module_{{moduleindex}}-segment_{{segmentindex}}_temperature">{{s.temperature}}</div> + / -
      <div class="edit" id="module_{{moduleindex}}-segment_{{segmentindex}}_duration">{{s.duration}}</div> + / - 
    {% endfor %} 
    <a class="modify" href="/modify_program?addsegment={{moduleindex}}">+</a>
    <div class="edit" id="cycles_{{moduleindex}}">{{m.cycles}}</div>
  </div>
{% endfor %}
</div>
"""

    def __init__(self):
      self.name = "ThermoTyp Program"
      self.modules = [TTModule()]

    def render(self):
      return Template(self.template).render(self.toDict())

    def toDict(self):
        mydata = { "name": self.name, "modules": []}
        for m in self.modules:
            mydata["modules"].append(m.toDict())

        return mydata

    def toJSON(self):
        return json.dumps(self.toDict())
    
    def toCSV(self):
        csv = ''
        max_segments = 0
        for m in self.modules:
           if len(m.segments) > max_segments:
              max_segments = len(m.segments)

        csv = "temp C, temp var, time (s), time var," * max_segments
        csv += "\n"
        
        for m in self.modules:
            for s in m.segments:
                csv += ",".join([str(s.temperature), str(s.temperature_increment), str(s.duration), str(s.duration_increment)]) + "," 
                
            if len(m.segments) < max_segments:
                csv += ",,,," * (max_segments - len(m.segments)) 
            csv += "\n"
        return csv


class TTModule(object):
    segments = []
    cycles = 0 
    name = ''

    def __init__(self):
        self.name = "New Module"
        self.cycles = 1
        self.segments = [TTSegment()]

    def toDict(self):
        mydata = dict( name = self.name, cycles = self.cycles, segments = [] )
        for s in self.segments:
            mydata["segments"].append(s.toDict())
        return mydata

class TTSegment(object):
    duration = 120 #duration in seconds 
    duration_increment = 0 #how much to increase, decrease 
    temperature = 24
    temperature_increment = 0
    
    def __init__(self):
        self.duration = 120 #duration in seconds 
        self.duration_increment = 0 #how much to increase, decrease 
        self.temperature = 24
        self.temperature_increment = 0
     
    def toDict(self):
        return self.__dict__

class ThermotypGUI(object):
    
    def __init__(self):
        self.program = TTProgram()

    #updating a single value within the program
    @cherrypy.expose
    def update_program(self, id, value):
        cherrypy.response.headers['Content-Type'] = 'text/html'
        #here is where we would do validation based on ID
        return value 

    #changing the actual structure of the program
    @cherrypy.expose
    def modify_program(self, link):
        cherrypy.response.headers['Content-Type'] = 'text/html'
        return "hello!"    

    #return the programs contents as a JSON
    @cherrypy.expose
    def json(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return self.program.toJSON() 

    @cherrypy.expose
    def csv(self):
        cherrypy.response.headers['Content-Type'] = 'text/csv'
        return self.program.toCSV()

    @cherrypy.expose
    def render(self):
        cherrypy.response.headers['Content-Type'] = 'text/html'
        return self.program.render()

    @cherrypy.expose
    def index(self):
        return """
<HTML>
<HEAD>

</HEAD>
<BODY>
<FORM name="program" id="program">""" + self.program.render() + """
</FORM>
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js"></script>
<script type="text/javascript" src="http://www.appelsiini.net/download/jquery.jeditable.mini.js"></script>
<script>

 $(document).ready(function() {
    $('.edit').editable('/update_program');
    $('.modify').click(function(ev) { 
      target = (ev.originalTarget)?ev.originalTarget:ev.srcElement; 
      $.get(target, function () { $('#program').load('/render') })
      alert(target);
      return false; 
      })
 });

 function rerender() {
    $('#program').load('/render');
 }
</script>
</BODY>
</HTML>
"""

 #def open_page():
#    webbrowser.open("http://127.0.0.1:8080/")

#config = {}
#cherrypy.engine.subscribe('start', open_page)
#cherrypy.tree.mount(ThermotypGUI(), '/', config=config)
#cherrypy.engine.start()
cherrypy.quickstart(ThermotypGUI())

