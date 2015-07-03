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
    url(r'^logs', 'dashboard.views.logs'),
    url(r'^classes', 'dashboard.views.classes'),
    url(r'^upload$', 'dashboard.views.upload_file'),
    url(r'register', 'dashboard.views.register'),
    url(r'^api/student/(?P<student_id>[0-9]{1,10})/?$', 'dashboard.views.display_student_score'),
    url(r'^accounts/register/$', 'dashboard.views.register_user'),
    url(r'^accounts/register_success/$', 'dashboard.views.register_success'),
    url(r'^login/$', 'dashboard.views.login_user', name="login"),
    url(r'^logout/$', 'dashboard.views.logout')

)

# /api/student/4