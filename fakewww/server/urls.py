from django.conf.urls import patterns, url

from .views import *

urlpatterns = patterns(
    '',
    url(r'^(?P<path>.*)$', default_webpage_view),
)
