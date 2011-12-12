import cherrypy

class TTProgram(object):
    modules = []

    def __init__(self):
      self.modules = []

    def toCSV(self):
        csv = ''
        max_segments = 0
        for m in self.modules:
           if len(m.segments) > max_segments:
              max_segments = len(m.segments)

        csv = "temp C, temp var, time (s), time var," * max_segment 
        csv += "\n"
        
        for m in self.modules:
            for s in m.segments:
                csv += ",".join(s.temperature, s.temperature_increment, s.duration, s.duration_increment) + "," 
                
            if len(m.segments) < max_segments:
                csv += ",,,," * (max_segments - len(m.segments)) 
            csv += "\n"


class TTModule(object):
    segments = []
    cycles = 0 
    name = ''

    def __init__(self):
        self.segments = []

class TTSegment(object):
    duration = 0 #duration in seconds 
    duration_increment = 0 #how much to increase, decrease 
    temperature = 24
    temperature_increment = 0
     
class ThermotypGUI(object):
    segments = []

    def index(self):
        return """
<HTML>
<HEAD>

</HEAD>
<BODY>
<FORM name="program">
<div class="programheader">
  <div class="edit" id="programid_1">Program 1</div><br>
</div>
<div class="moduleheader">
  <a href="#removemodule">X</a><br>
  <div class="edit" id="moduleid_1">MODULE 1</div><br>
  <a href="#addmodule">[+]</a><br>
</div>

<div class="modulebody">
  <div class="segment">
    <div class="edit" id="targettemp_1">95</div><br>
    <div class="edit" id="cycletime_1">2:00</div><br>
  </div>
  <a href="#addsegment">[+]</a><br>
  <div class="edit" id="numcycles_1">3</div><br>
</div>
</FORM>
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js"></script>
<script type="text/javascript" src="http://www.appelsiini.net/download/jquery.jeditable.mini.js"></script>
<script>
 $(document).ready(function() {
     $('.edit').editable('/update_program');
 });
</script>
</BODY>
</HTML>
"""
    index.exposed = True

    def update_program(self):
        cherrypy.response.headers['Content-Type'] = 'text/html'
        return "hello world!"


    update_program.exposed = True


def open_page():
    webbrowser.open("http://127.0.0.1:8080/")

config = {}
cherrypy.engine.subscribe('start', open_page)
cherrypy.tree.mount(ThermotypGUI(), '/', config=config)
cherrypy.engine.start()
