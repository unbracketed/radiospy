"""
Various breakdowns station playlist data
"""
from django.shortcuts import render_to_response, get_object_or_404
from radiospy.playlist.models import Playlist, Channel

def now_playing(request):
    now_playing = [Playlist.objects.filter(channel=c).latest() for c in Channel.objects.active()]
    return render_to_response('stats/now_playing.html',locals())
    
def station_playlist(request,station_id):
    station = get_object_or_404(Channel,pk=station_id)
    playlist = Playlist.objects.filter(channel=station)
    return render_to_response('stats/station_playlist.html',locals())
