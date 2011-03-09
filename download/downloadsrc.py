#!/usr/bin/env python
#coding: utf-8

import urllib
import json
import sys

try: apiurl = "http://sharesrc.appspot.com/api?token=%s"% sys.argv[1]
except:
	print "Usage $ python downloadsrc.py [token]"
	print "please write token of code at 'sharesrc'."
	print "ex): $ python downloadsrc.py x4jtk4hcaq6j3t34bradpe72jaf1yh"
	print "       -> you can downlaod about file."
	
print "token : %s" % sys.argv[1]
print "Downloading..."
data = json.loads(urllib.urlopen(apiurl).read())

file = data["title"]
body = data["src"]
print "Writing..."
f = open(file,"w")
f.write(body.encode("utf-8"))
f.close()
print "Completed."
