import re #regex

import cherrypy
import webbrowser
import json
from jinja2 import Template

#our Program class
class TTProgram(object):
    name =''
    modules = []
    #define the name of the program and what modules exist

    #this template is the "guts" of the GUI
    template = """
<div class="edit programheader" id="programname">{{name}}</div>
<div class="programbody">
{% for m in modules %}
  {% set moduleindex = loop.index %}
  <div class="moduleheader">
    <a class="modify" href="/modify_program?removemodule={{moduleindex}}">[X]</a>
    <div class="edit" id="module_{{moduleindex}}_name">{{m.name}}</div>
    <a class="modify" href="/modify_program?addmodule={{moduleindex}}">[+]</a>
  </div>
  <div class="modulebody">
    {% for s in m.segments %}
      {% set segmentindex = loop.index %}
      <div class="edit" id="module_{{moduleindex}}_segment_{{segmentindex}}_temperature">{{s.temperature}}</div>
      <div class="increment" id="module_{{moduleindex}}_segment_{{segmentindex}}_temperatureincrement">
         <div id="increment_value">{{s.temperatureincrement}}</div>
         <a name="up">+</a>
         <a name="down">-</a>
      </div>
      <div class="edit" id="module_{{moduleindex}}_segment_{{segmentindex}}_duration">{{s.duration}}</div>
      <div class="increment" id="module_{{moduleindex}}_segment_{{segmentindex}}_durationincrement">
         <div id="increment_value">{{s.durationincrement}}</div>
         <a name="up">+</a>
         <a name="down">-</a>
      </div>
    {% endfor %} 
    <a class="modify" href="/modify_program?addsegment={{moduleindex}}">+</a>
    <div class="edit" id="cycles_{{moduleindex}}">{{m.cycles}}</div>
  </div>
{% endfor %}
</div>
"""

    #what we get with a fresh program
    def __init__(self):
      self.name = "ThermoTyp Program"
      self.modules = [TTModule()]

    #render the template via Jinja2
    def render(self):
      return Template(self.template).render(self.toDict()) 

    #convert the program and its subclasses to a dictionary
    #appropriate for JSON serialization
    def toDict(self):
        mydata = { "name": self.name, "modules": []}
        for m in self.modules:
            mydata["modules"].append(m.toDict())

        return mydata

    #return a JSON-ized form of the program
    def toJSON(self):
        return json.dumps(self.toDict())
    
    #return a CSV of the program
    def toCSV(self):
        csv = ''
        max_segments = 0
        
        #find the longest segment, this will determine the CSV width
        for m in self.modules:
           if len(m.segments) > max_segments:
              max_segments = len(m.segments)

        #create the CSV header
        csv = "temp C, temp var, time (s), time var," * max_segments
        csv += "\n"
        
        #iterate through the modules and build 1 row per module
        for m in self.modules:
            for s in m.segments:
                csv += ",".join([str(s.temperature), str(s.temperatureincrement), str(s.duration), str(s.durationincrement)]) + "," 
                
            #pad out any empty cells
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
    durationincrement = 0 #how much to increase, decrease 
    temperature = 24
    temperatureincrement = 0
    
    def __init__(self):
        self.duration = 120 #duration in seconds 
        self.durationincrement = 0 #how much to increase, decrease 
        self.temperature = 24
        self.temperatureincrement = 0
     
    def toDict(self):
        return self.__dict__

class ThermotypGUI(object):
    
    def __init__(self):
        self.program = TTProgram()
        #initialize an empty program on startup
        #this is where you would load from a CSV if you wanted to

    #updating a single value within the program
    @cherrypy.expose
    def update_program(self, id, value):
        cherrypy.response.headers['Content-Type'] = 'text/html'
        
        if (id == "programname"):
            self.program.name = value
        elif (re.match("module_(\d)", id)):
            #we're updating a module property
            module_index = int(re.match("module_(\d)", id).group().split("_")[1])-1
            module = self.program.modules[module_index]
            
            therest = id.split("_")[2:]
            if module.__dict__.has_key(therest[0]):
                module.__dict__[therest[0]] = value
            
            if (therest[0] == "segment"):
                segment_index = int(therest[1])-1
                prop = therest[2]
                seg = module.segments[segment_index].__dict__
            
                if seg.has_key(prop):
                    if value[0] == "+":
                        seg[prop] = int(seg[prop]) + int(value[1:])
                        value = seg[prop]
                    elif value[0] == "-":
                        seg[prop] = int(seg[prop]) - int(value[1:])
                        value = seg[prop]
                    else:
                        seg[prop] = value
        
        return str(value)

    #changing the actual structure of the program
    @cherrypy.expose
    def modify_program(self, **vars):
        cherrypy.response.headers['Content-Type'] = 'text/html'
        for k in vars.keys():
            index = int(vars[k]) - 1
            if k == "removemodule":
                if len(self.program.modules) == 1:
                    return "false"
                self.program.modules.pop(index)
            if k == "addmodule":
                self.program.modules.insert(index + 1, TTModule())
            if k == "addsegment":
                self.program.modules[index].segments.append(TTSegment())
                
        return "true"    

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
        return self.program.render() + "<script>activate_widgets()</script>";

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

#this function changes the sparse template into something with actual actions
#the three types are "edit" (editable field), "modify" (program structure change)
#and "increment" (a +/- modification)
function activate_widgets() {
    $('.edit').editable('/update_program');
    $('.modify').click(function(ev) { 
      ev.preventDefault();
      target = (ev.originalTarget)?ev.originalTarget:ev.srcElement; 
      $.get(target, function () { $('#program').load('/render'); })
      return false; 
      });
      
    $('.increment > a').each(function() {
      id = $(this).parent().attr('id');
      value_div = $(this).parent().find("#increment_value");
      value = parseInt(value_div.html());
      if ($(this).attr('name') == "up") {
        $(this).attr("href", "/update_program?id="+id+"&value=+1");
      }
      if ($(this).attr('name') == "down") {
        $(this).attr("href", "/update_program?id="+id+"&value=-1");
      }
      $(this).click(function(ev) {
        ev.preventDefault();
        target = (ev.originalTarget)?ev.originalTarget:ev.srcElement;
        $(target).parent().find("#increment_value").load($(target).attr("href"));
      });
    });
 };

 $(document).ready(activate_widgets);

</script>
</BODY>
</HTML>
"""

def open_page():
    webbrowser.open("http://127.0.0.1:8080/")

config = {}
cherrypy.engine.subscribe('start', open_page)
cherrypy.tree.mount(ThermotypGUI(), '/', config=config)
cherrypy.engine.start()
#cherrypy.quickstart(ThermotypGUI())
#uncomment this for debugging

