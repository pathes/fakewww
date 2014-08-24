from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^__admin/', include(admin.site.urls)),
    url(r'^__admindocs/', include('django.contrib.admindocs.urls')),
    url(r'^__generator/', include('generator.urls')),
    url(r'^', include('server.urls')),
)
