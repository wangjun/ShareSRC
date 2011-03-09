# -*- coding: utf-8 -*-
import os
import random
from cgi import escape
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util, template
from django.utils import simplejson

# DATASTORE SETTING
class Codes(db.Model):
	TITLE = db.StringProperty()
	SRC = db.TextProperty()
	TOKEN = db.StringProperty() # <- md5 hash
	FORKED = db.StringProperty()

# TOP PAGE
class MainHandler(webapp.RequestHandler):
	def get(self):
		items = {
			"fork":"",
			"title_value":"",
			"src_value":"",
			"token":self.maketoken(),
			"forked":False
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
				items["forked"] = forkdata["token"]
			
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
				item["token"] = data.TOKEN
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

# ADD DATA PAGE
class RegistoryHandler(webapp.RequestHandler):
	def post(self):
		title = escape(self.request.get("title"))
		src = escape(self.request.get("src"))
		token = escape(self.request.get("token"))
		forked = escape(self.request.get("forked"))
		
		regist = Codes()
		regist.TITLE = title
		regist.SRC = src
		regist.TOKEN = token
		regist.FORKED = forked
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
				items["token"] = data.TOKEN
				items["src"] = ""
				i = 1
				for c in data.SRC.split("\n"):
					items["src"] += "<span style='background:#aaa;border-right:1px solid #000;padding:0px;padding-left:7px;'>%s</span> %s" % (str(i).ljust(3),c)
					i += 1
				items["fork_link"] = "/?fork=%s" % data.TOKEN
				if data.FORKED == "False":
					items["forked"] = "original"
				elif data.FORKED == "":
					items["forked"] = "original"
				else:
					for data2 in regist:
						forkedtoken = data2.TOKEN
						if data.FORKED == forkedtoken:
							forkedtitle = data2.TITLE
							result = True
							break
						else: result = False
					if result:
						items["forked"] = "<a href='%s'>%s</a>からfork" % ("/print?t=%s" % data.FORKED.encode('utf-8'), forkedtitle.encode('utf-8'))
					else:
						items["forked"] = "original"
				
				
		path = os.path.join(os.path.dirname(__file__),'printout.html')
		self.response.out.write(template.render(path,items))

# VIEW PAGE
class ViewHandler(webapp.RequestHandler):
	def get(self):
		items = {"contents":""}
		
		regist = db.GqlQuery("SELECT * FROM Codes")
		tokens = sorted([i.TOKEN for i in db.GqlQuery("SELECT * FROm Codes")])
		
		for data in regist:
			for token in tokens:
				if data.TOKEN == token:
					i = 1
					cont = ""
					for c in data.SRC.split("\n"):
						cont += "<span style='background:#aaa;border-right:1px solid #000;padding:0px;padding-left:7px;'>%s</span> %s" % (str(i).ljust(4),c)
						i += 1
					contents = """<div id="stitle" style="float:left;"><a href="%s">%s</a></div>
							<div align="right" style="float:right;margin-top:15px;"><a href="%s">forkする</a></div>
							<div id="code" style="height:auto;text-align:left;clear:both;">
								<pre class="prettyprint" style="border:none;padding:0px;margin:0px;font-size:16px;">%s</pre>
							</div>""" % ('/print?t=%s'%data.TOKEN.encode('utf-8'), data.TITLE.encode('utf-8'), '/?fork=%s'%data.TOKEN.encode('utf-8'), cont.encode('utf-8'))
					items["contents"] += contents
						
		path = os.path.join(os.path.dirname(__file__),'contents.html')
		self.response.out.write(template.render(path,items))
		
#CSS
class SupportFile(webapp.RequestHandler):
	def get(self):
		self.response.headers["Content-Type"] =  "text"
		file = self.request.get("file")
		self.response.out.write(open(file,"r").read())
		
class About(webapp.RequestHandler):
	def get(self):
		self.redirect("http://sharesrc.appspot.com/print?t=x4jtk4hcaq6j3t34bradpe72jaf1yh")
		
class API(webapp.RequestHandler):
	def get(self):
		self.response.headers["Content-Type"] = "application/json"		
		token = self.request.get("token")
		
		regist = db.GqlQuery("SELECt * FROm Codes")
		for data in regist:
			if data.TOKEN == token:
				returndata = {}
				returndata["title"] = data.TITLE
				returndata["src"] = data.SRC
				returndata["token"] = data.TOKEN
				result = True
				break
			else: result = False
			
		if result:
			self.response.out.write(simplejson.dumps(returndata))
		else:
			self.response.out.write("No mutch '%s' TOKEN!!" % token)


def main():
	application = webapp.WSGIApplication([
							('/', MainHandler),
							('/f',SupportFile),
							('/registory',RegistoryHandler),
							('/print',PrintHandler),
							('/view',ViewHandler),
							('/about',About),
							('/api',API)],debug=True)
	util.run_wsgi_app(application)
	
if __name__ == '__main__':
	main()