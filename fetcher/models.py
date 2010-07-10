import datetime
from django.db import models

from radiospy.fetcher.constants import FETCH_STATUS_CHOICES, FETCH_STATUS_SUCCESS
from radiospy.playlist.models import Channel

class FetchResult(models.Model):
    """
    Records that an attempt was made to fetch metadata about the current playing
    audio on a Channel
    """
    channel = models.ForeignKey(Channel,db_index=True)
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    status = models.BooleanField()
    status_flag = models.IntegerField(choices=FETCH_STATUS_CHOICES,default=FETCH_STATUS_SUCCESS) 
    
class FailedFetch(models.Model):
    """
    Whenever a metadata fetch appears to fail an instance will be created to hold
    any data about what might have gone wrong.
    
    data will be a pickled python object
    """
    fetch = models.ForeignKey(FetchResult)
    #TODO: find pickle field 
    data = models.TextField()
    