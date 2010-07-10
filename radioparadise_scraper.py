#!/usr/bin/env python
from urllib import urlopen

from BeautifulSoup import BeautifulSoup

RP_HISTORY_URL = "http://www.radioparadise.com/content.php?name=Playlist&more=true"

p = urlopen(RP_HISTORY_URL)
soup = BeautifulSoup(p.read())
#print soup
p.close()

