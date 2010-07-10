from django.conf.urls.defaults import *

urlpatterns = patterns('radiospy.stats.views',
    # Example:
    # (r'^radiospy/', include('radiospy.foo.urls')),
    url(r'^$','now_playing',name='stats_now_playing'),
    url(r'^station/(?P<station_id>\d+)/playlist/$','station_playlist',name='stats_station_playlist'),
)
