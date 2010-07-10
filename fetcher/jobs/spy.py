import re
from twisted.internet import protocol, reactor
from twisted.internet import task
from django_extensions.management.jobs import BaseJob

from radiospy.fetcher.shoutcast import ShoutcastMetadataPeeker
from radiospy.fetcher.streams import StreamHandler
from radiospy.playlist.models import Channel

#TODO:
# try all streams until one succeeds


class Job(BaseJob):
    help = "run the net station metadata fetcher"
    
    def execute(self):
        
        def update_channels():
            print "updating channels"
            update_channels = Channel.objects.filter(active=True)
            
            #grab their stream address
            for i,channel in enumerate(update_channels):
                print "handling channel %s" % str(channel)
                sh = StreamHandler(channel.stream_url)
                
                #TODO: handle no valid URLs
                
                for host,port,path in sh.urls:       
                    mo = re.compile(r'^([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])$').match(host)
                    if mo:
                        print 'detected IP, going to next'
                        continue
                    
                    else:
                        
                        #TODO handle timeout
                    
                        #TODO - shoutcast client doesn't like IP addr?
                        
                        #TODO record if a valid connect addr is not found
                        
                        #TODO: cache the actual connect address, try it first next time
                        
                        #TODO: how to catch connection failure and try other stream addresses
                        
                        #provide a valid default path to the Shoutcast client
                        if not len(path):
                            path = '/'
                        print "connecting %s %s %s" % (host,port,path)
                        protocol.ClientCreator(reactor, ShoutcastMetadataPeeker, channel, path=path).connectTCP(host,int(port))
                        
                        break
        
        print "starting reactor"
        loop = task.LoopingCall(update_channels)
        loop.start(60)
        reactor.run()