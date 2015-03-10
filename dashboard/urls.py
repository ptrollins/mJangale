__author__ = 'ptrollins'

from django.conf.urls import patterns, include, url
from django.contrib import admin
# from dashboard import views

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'dashboard.views.index'),
    url(r'^index', 'dashboard.views.index'),
    url(r'^dashboard', 'dashboard.views.dashboard'),
    url(r'^usage', 'dashboard.views.usage'),
    url(r'^scores', 'dashboard.views.scores'),
    url(r'^class', 'dashboard.views.classes'),
    url(r'^upload$', 'dashboard.views.upload_file'),
)
