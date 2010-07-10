from django.contrib import admin
from radiospy.playlist.models import Producer,Channel,Show,Track,Playlist

admin.site.register(Producer)
admin.site.register(Show)
admin.site.register(Channel)
admin.site.register(Track)
admin.site.register(Playlist)


