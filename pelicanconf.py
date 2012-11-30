#!/usr/bin/env python
# -*- coding: utf-8 -*- #

AUTHOR = u"Thomas Chiroux"
SITENAME = u"chiroux.org"
SITEURL = 'http://chiroux.org'
#THEME = 'notmyidea'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = 'fr'

#GITHUB_URL = 'http://github.com/ametaireau/'
#DISQUS_SITENAME = "blog-notmyidea"
PDF_GENERATOR = False
REVERSE_CATEGORY_ORDER = True
LOCALE = "C"
DEFAULT_PAGINATION = 4

FEED_ALL_RSS = 'feeds/all.rss.xml'
CATEGORY_FEED_RSS = 'feeds/%s.rss.xml'

# static paths will be copied under the same name
STATIC_PATHS = ["media", ]

# Blogroll
LINKS = (('afpy', 'http://www.afpy.org/'),
         ('april', 'http://www.april.org/'),
         ('lqdn', 'http://www.laquadrature.net/fr'),)

# Social widget
SOCIAL = (('twitter', 'https://twitter.com/ThomasChiroux'),
          ('google+', 'https://plus.google.com/113683015116617526200/'),
          ('github', 'https://github.com/ThomasChiroux'))

DEFAULT_PAGINATION = 10
