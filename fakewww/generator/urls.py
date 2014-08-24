from django.conf.urls import patterns, url

from .views import *

urlpatterns = patterns(
    '',
    url('^$', generator_view, name='generator'),
    url('^domains$', domain_list_view, name='domain_list'),
    url('^domain/(?P<domain>.*)$', domain_view, name='domain'),
)
