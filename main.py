# -*- coding: utf-8 -*-
import os
import random
from cgi import escape
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util, template


# DATASTORE SETTING
class Codes(db.Model):
	TITLE = db.StringProperty()
	SRC = db.TextProperty()
	TOKEN = db.StringProperty() # <- md5 hash

# TOP PAGE
class MainHandler(webapp.RequestHandler):
	def get(self):
		items = {
			"fork":"",
			"title_value":"",
			"src_value":"",
			"token":self.maketoken()
		}
		forked = self.request.get("fork")
		if forked == "":
			pass
		else:
			forkdata = self.getdata(forked)
			if forkdata["result"] == False:
				items["fork"] = "<p>データがありません</p>"
			else:
				items["fork"] = "<p><a href='%s'>%s</a>からfork</p>" % ("/print?t=%s" % forked.encode("utf-8"), forkdata["title"].encode("utf-8"))
				items["title_value"] = forkdata["title"]
				items["src_value"] = forkdata["src"]
			
		path = os.path.join(os.path.dirname(__file__),'index.html')
		self.response.out.write(template.render(path,items))
		
	def getdata(self, tokendata):
		""" Get Code Data, and return contents."""
		item = {"result":False}
		codes = db.GqlQuery("SELECT * FROM Codes")
		for data in codes:
			token = data.TOKEN
			if token == tokendata:
				item["title"] = data.TITLE
				item["src"] = data.SRC
				item["result"] = True
				break
			else: item["result"] = False
		
		return item
		
	def maketoken(self):
		string = ""
		base = "abcdefghijklmnopqrstuvwxyz1234567890"
		for i in range(30):
			x = random.choice(list(base))
			string += x
		return string	

# ADD DATA PAHE
class RegistoryHandler(webapp.RequestHandler):
	def post(self):
		title = escape(self.request.get("title"))
		src = escape(self.request.get("src"))
		token = escape(self.request.get("token"))
		
		regist = Codes()
		regist.TITLE = title
		regist.SRC = src
		regist.TOKEN = token
		regist.put()
		
		self.redirect("/print?t=%s"% token)
		
	def prints(self, string):
		self.response.out.write(string)
		
# PRINTOUT PAGE
class PrintHandler(webapp.RequestHandler):
	def get(self):
		items = {}
		token = self.request.get("t")
		
		regist = db.GqlQuery("SELECT * FROM Codes")
		for data in regist:
			datatoken = data.TOKEN
			if datatoken == token:
				items["title"] = data.TITLE
				items["src"] = data.SRC
				items["fork_link"] = "/?fork=%s" % data.TOKEN
				
				
				
		path = os.path.join(os.path.dirname(__file__),'printout.html')
		self.response.out.write(template.render(path,items))

# VIEW PAGE
class ViewHandler(webapp.RequestHandler):
	def get(self):
		items = {"contents":""}
		
		regist = db.GqlQuery("SELECT * FROM Codes")
		for data in regist:
			contents = """<div id="stitle" style="float:left;"><a href="%s">%s</a></div>
					<div align="right" style="float:right;margin-top:15px;"><a href="%s">forkする</a></div>
					<div id="code" style="height:auto;text-align:left;clear:both;">
						<pre style="text-align:left;" name="code" class="%s">%s</pre>
					</div>""" % ('/print?t=%s'%data.TOKEN.encode('utf-8'), data.TITLE.encode('utf-8'), '/?fork=%s'%data.TOKEN.encode('utf-8'), self.getlang(data.SRC.encode('utf-8')), data.SRC.encode('utf-8'))
			items["contents"] += contents
		
		path = os.path.join(os.path.dirname(__file__),'contents.html')
		self.response.out.write(template.render(path,items))
		
	def getlang(self,text):
		setting = {"C++":"cpp","Cs":"c-charp","css":"css","delphi":"delphi","java":"java","javascript":"js","php":"php","python":"py",
				"ruby":"rb","sql":"sql","vb":"vb","html":"html","xml":"xml"}
		for lang in setting.keys():
			if lang in text:
				result =  setting[lang]
				break
			else: result = False
			
		if result == False:
			return "text"
		else: return result
		
#CSS
class SupportFile(webapp.RequestHandler):
	def get(self):
		self.response.headers["Content-Type"] =  "text/file"
		file = self.request.get("file")
		self.response.out.write(open(file,"r").read())
		
def main():
	application = webapp.WSGIApplication([
							('/', MainHandler),
							('/f',SupportFile),
							('/registory',RegistoryHandler),
							('/print',PrintHandler),
							('/view',ViewHandler)],debug=True)
	util.run_wsgi_app(application)
	
if __name__ == '__main__':
	main()