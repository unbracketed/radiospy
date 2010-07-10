#!/usr/bin/env python
import os
from urllib2 import urlopen
import urlparse
from twisted.internet.error import TimeoutError
from radiospy.fetcher.pls import fetchAndParsePLS

class StreamHandler:
    """
    Negotiates the content for a public stream address. This may include
    handling playlist files that include several available stream addresses.
    The goal is to have a valid TCP Host:Port that can be handed off to the ShoutcastClient
    """
    
    def __init__(self,*args,**kwargs):
        stream_url = args[0]
        self.urls = []        
        #determine format from extension
        base,ext = os.path.splitext(urlparse.urlsplit(stream_url)[2])
        print ext
        
        def network_bitz(url):
            netloc = urlparse.urlparse(url)
            return (netloc.hostname,netloc.port,netloc[2],)
        
        #PLS Handler
        if ext == '.pls':
            try:
                self.urls = list(map(network_bitz,fetchAndParsePLS(stream_url)))
                print self.urls
            except TimeoutError:
                print "Timeout error on %s" % stream_url
                
        
        #M3U Handler
        elif ext == '.m3u':
        
            resp = urlopen(stream_url)
            meta = resp.info()
            print meta
            if 'Content-Length' in meta:
                print type(meta['Content-Length'])
                if meta['Content-Length'].isdigit():
                    print 'len %d' % int(meta['Content-Length'])
                    
                #parse file for the extension type
                
                for line in resp.readlines():
                    print line
                    line = line.rstrip('\n')
            
                    if line.startswith('#') or len(line.strip()) == 0:
                        continue
            
                    if line.startswith('http://'):
                        
                        netloc = urlparse.urlparse(line)
                        host = netloc.hostname
                        port = netloc.port
                        self.urls.append((host,port,netloc[2]))
                        print "got netloc %s %s %s" % (host,port,netloc[2])
                                
                    
if __name__ == '__main__':
    import sys
    sh = StreamHandler(sys.argv[1])
    
        
    