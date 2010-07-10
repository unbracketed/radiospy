import datetime
from django.db import models
from django.template.defaultfilters import date
from radiospy.playlist.constants import DEFAULT_CHANNEL_NAME, DEFAULT_SHOW_NAME


class Producer(models.Model):
    """
    A Producer is meant to represent the "site" or "brand" associated with
    one or more net radio stations. For example, SomaFM produces several
    channels. In many cases a Producer will only have one channel
    """
    name = models.CharField(max_length=255)
    homepage = models.URLField(verify_exists=False)
    description = models.TextField()
    
    def __unicode__(self):
        return self.name


class ChannelManager(models.Manager):
    def active(self):
        return self.filter(active=True)
    
class Channel(models.Model):
    """
    A Channel is analogous to what is traditionally a station. A channel is what
    listeners tune to (connect with). The content on a channel can be
    subdivided into Shows
    """
    name = models.CharField(max_length=255,default=DEFAULT_CHANNEL_NAME)
    producer = models.ForeignKey(Producer)
    tagline = models.TextField(blank=True)
    stream_url = models.URLField(verify_exists=False)
    active = models.BooleanField(default=True)
    
    objects = ChannelManager()
    
    
    def __unicode__(self):
        if self.name == DEFAULT_CHANNEL_NAME:
            return unicode(self.producer.name)
        return u"%s: %s" % (self.producer.name,self.name)
            
    
class Show(models.Model):
    """
    A timed segment of content on a channel.
    """
    name = models.CharField(max_length=255,default=DEFAULT_SHOW_NAME)
    producer = models.ForeignKey(Producer)
    channel = models.ForeignKey(Channel)
    
    #TODO: shows have a schedule
    #investigate django-scheduler or django-swingtime
    
    def __unicode__(self):
        return self.name
    
        
class Track(models.Model):
    """
    A song played on a net radio station
    """
    raw_name = models.CharField(max_length=255)
    MBID = models.CharField(max_length=40,blank=True)
    artist = models.CharField(max_length=128,blank=True)
    name = models.CharField(max_length=128,blank=True)
    
    def __unicode__(self):
        if len(self.artist) and len(self.name):
            return unicode("%s - %s" % (self.artist,self.name,))
        return self.raw_name
    
    @property
    def title_display(self):
        return "%s - %s" % (self.artist,self.name)
    
class Playlist(models.Model):
    """
    Represents a chronological log of tracks played on a station
    """
    channel = models.ForeignKey(Channel)
    track = models.ForeignKey(Track)
    time = models.DateTimeField(default=datetime.datetime.now)
    
    class Meta:
        get_latest_by = 'time'
        ordering = ('-time',)
    
    def __unicode__(self):
        return "%s at %s on %s" % (self.track.title_display,date(self.time,"g:i"),str(self.channel))