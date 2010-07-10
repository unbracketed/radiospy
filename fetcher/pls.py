#
# "@(#) $Id: PLS.py,v 1.1.1.1 2006-07-27 03:16:08 gioshe Exp $"
#
# This work is released under the GNU GPL, version 2 or later.
#
# handle .pls files
#
import httplib, urllib, re

def http_head(host,port,fileName):
	h = httplib.HTTP(host,port)
	h.putrequest('HEAD',fileName)
	h.putheader('Accept','text/html')
	h.putheader('Accept','text/plain')
	h.putheader('Accept','*/*')
	h.endheaders()
	return h.getreply()

def http_get(host,port,fileName):
	h = httplib.HTTP(host,port)
	h.putrequest('GET',fileName)
	h.putheader('Accept','text/html')
	h.putheader('Accept','text/plain')
	h.putheader('Accept','*/*')
	h.endheaders()
	errCode, errMessage, headers = h.getreply()
	if errCode==200 or errCode==302:
		f = h.getfile()
		return f.read()
	return None

def fetchAndParsePLS(url):
	(type,path) = urllib.splittype(url)
	(hostport,path) = urllib.splithost(path)
	(host,port) = urllib.splitport(hostport)
	if port==None: port = 80
	s = http_get(host,port,path)
	if s!=None:
		#print s
		return parsePLS(s)
	return None

def readAndParsePLS(url):
	pls = open(url).read()
	return parsePLS(pls)

def parsePLS(pls):
	flags = re.MULTILINE | re.IGNORECASE
	mo = re.search(r"^numberofentries\=(\d+)$",pls,flags)
	if mo:
		numberOfEntries = int(mo.group(1))
		streams = []
		for i in range(1,numberOfEntries+1):
			mo = re.search(r"File%d\=(.+)$" % i,pls,flags)
			if mo:
				streams.append(mo.group(1))
		return streams
	return None

if __name__=='__main__':
	print fetchAndParsePLS("http://somafm.com/secretagent.pls")

