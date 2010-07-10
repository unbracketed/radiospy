import os
if not 'DJANGO_SETTINGS_MODULE' in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'radiospy.settings'

import datetime
import logging
from urllib2 import HTTPError

import musicbrainz2.webservice as ws
from musicbrainz2.webservice import TrackFilter
from twisted.protocols.shoutcast import ShoutcastClient

    
from django.core.exceptions import ObjectDoesNotExist

from radiospy.fetcher.constants import *
from radiospy.fetcher.models import FailedFetch, FetchResult
from radiospy.playlist.models import Track, Playlist

logging.basicConfig(filename='shoutcast_reader',level=logging.DEBUG)


class ShoutcastMetadataPeeker(ShoutcastClient):
    """
    Utilizies the Twisted Shoutcast Client for connecting to
    a net radio stream, identifying metadata and parsing it into
    name,value pairs. Once the meta is handed off this class then attempts
    to extract a relevant artist and title for use in a lookup to the
    MusicBrainz music data respository.
    """
    
    def __init__(self,channel,path="/"):
        
        self.channel = channel
        self.path = path
        self.got_metadata = False
        self.metaint = None
        self.metamode = "mp3"
        self.databuffer = ""
    
    def gotMetaData(self, data):
        
        q = ws.Query()
        
        
        #metadata track Brewer & Shipley - Witchi-Tai-To
        #[(u'Brewer & Shipley - Witchi', u'Tai-To'), (u'Brewer & Shipley - Witchi-Tai', u'To')]
        #No valid MB results
        #=== EXCEPTION local variable 'track' referenced before assignment
        #meta: [('StreamTitle', 'Brewer & Shipley - Witchi-Tai-To'), ('StreamUrl', 'http://www.radioparadise.com/graphics/covers/m/B00005MJYP.jpg')]

        
        try:
            try_list = self.track_from_metadata(data)
            print try_list
            if len(try_list):
                
                #TODO: there should be a "best bet" match. if something
                #fails in the loop, default to the best bet match
                track = None
                for artist,title in try_list:
                    
                    #TODO - match track from local data first before
                    #  doing MB lookup
                    
                    try:
                        res = q.getTracks(TrackFilter(title=title,artistName=artist))
                    except HttpError, e:
                        logging.warning("MusicBrainz getTracks : %s : %s : %s" % (e,artist,title,))
                    except Exception, e:
                        logging.error("MusicBrainz getTracks : %s : %s : %s" % (e,artist,title,))
                    
                    if len(res) == 0 or max([r.score for r in res]) < MUSICBRAINZ_TRACK_RESULT_SCORE_LOW:
                        
                        #if MB lookup fails, try others?
                        
                        logging.info("MusicBrainz track not found: %s %s" % (artist,title,))
                        
                        #we can be reasonably sure about artist,title
                    
                        if len(try_list) == 1 or len(res):
                            track,created = Track.objects.get_or_create(artist=artist,name=title)
                        
                            if created:
                                track.save()
                        else:
                            continue
                    
                    else:    
                        #we seem to have good MB results
                        try:
                            
                            #TODO: try track from cache, no need for playlist lookup if track in cache
                            
                            track = Track.objects.get(MBID=res[0].track.id)
                        except ObjectDoesNotExist:
                            
                            track = Track(MBID = res[0].track.id,
                                          artist = res[0].track.artist.name,
                                          name = res[0].track.title)
                            
                            track.save()
                            
                            #TODO cache track 
                            
                            print "stored track %s" % (track.title_display)
                            
                    #TODO fix dates ***********
                    #TODO assume playlist instance already exists if track was in cache
                    if track:
                        pl,created = Playlist.objects.get_or_create(channel=self.channel,track=track,time__lte=datetime.datetime.now())
                        if created:
                            pl.save()
                    else:
                        print "could not resolve track"
                        
            else:
                #TODO: no valid track data in metadata
                raise Exception
            
                
        except Exception, e:
            #TODO: record metadata error
            #differentiate between malformed and no match?
            print "=== EXCEPTION %s" % e
        
        finally:
            print "meta:", data
            self.transport.loseConnection()
        
    def gotMP3Data(self, data): pass

    def track_from_metadata(self,data):
        #sample from RadioParadise stream
        #[('StreamTitle', 'Cocteau Twins - Road, River And Rail'), ('StreamUrl', 'http://www.radioparadise.com/graphics/covers/m/B00000DRAX.jpg')]
        
        #TODO: handle encoding properly
        #metadata track Sigur R?s - Med Sud I Eyrum
        #['Sigur R\xffs ', ' Med Sud I Eyrum']
        #=== EXCEPTION 'ascii' codec can't decode byte 0xff in position 7: ordinal not in range(128)
        #meta: [('StreamTitle', 'Sigur R\xffs - Med Sud I Eyrum'), ('StreamUrl', '')]


        #TODO: look for station tags
        #ex: meta: [('StreamTitle', '~+ [P] Hot 108 Jamz Promo +~ - ~+ [P] Leads All +~'), ('StreamUrl', '')]
        #ex: Big Url (soma frm)
        
        track = ''
        for item in data:
            if item[0] == 'StreamTitle':
                track = item[1]
                break
        print 'metadata track %s' % track   
        
    
        #TODO: try swapping ` for '
        
    
        #   detect multiple hyphens
        if len(track):
            parts = track.split('-')
            if len(parts) < 2:
                #TODO
                return []
            elif len(parts) == 2:
                print parts
                return ((unicode(parts[0].strip()),unicode(parts[1].strip()),),)
            else:
                return [ (unicode('-'.join(parts[:i]).strip()),unicode('-'.join(parts[i:]).strip()),) for i in range(1,len(parts)) ]
        return []
        
    def handleResponse(self,response):
        print response
        
        
if __name__ == '__main__':
    class Test(ShoutcastClient):
        def gotMetaData(self, data): print "meta:", data
        def gotMP3Data(self, data): pass
    
    from twisted.internet import protocol, reactor
    import sys
    
    pc = protocol.ClientCreator(reactor, ShoutcastMetadataPeeker, None, path=sys.argv[3])
    pc.connectTCP(sys.argv[1], int(sys.argv[2]))
    reactor.run()

