__author__ = 'ptrollins'

from django.conf.urls import patterns, include, url
from django.contrib import admin
from dashboard.forms import CustomChangeForm, CustomSetPasswordForm, CustomPasswordResetForm
from django.contrib.auth import views as auth_views
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
    url(r'^logout/$', 'dashboard.views.logout'),
    url(r'^request_token', 'dashboard.views.request_token'),
    url(r'^generate_token', 'dashboard.views.generate_token'),
    url(r'^password_change/$', 'django.contrib.auth.views.password_change', {'template_name': 'auth/password_change_form.html', 
                                                                             'password_change_form':CustomChangeForm}),
    
    url(r'^password/change/$',
                    auth_views.password_change,
                    name='password_change'),
    url(r'^password/change/done/$',
                    'dashboard.views.password_changed',
                    name='password_change_done'),
    url(r'^password/reset/$',
                    auth_views.password_reset,
                    name='password_reset'),
    url(r'^password/reset/done/$',
                    auth_views.password_reset_done,
                    name='password_reset_done'),
                       
    url(r'^password/reset/complete/$',
                    auth_views.password_reset_complete,
                    name='password_reset_complete'),
                       
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
                    auth_views.password_reset_confirm,
                    name='password_reset_confirm'),

      #and now add the registration urls
    url(r'', include('registration.backends.default.urls')),
    url(r'^resetpassword/passwordsent/$', 'django.contrib.auth.views.password_reset_done', {'template_name': 'registration/password_reset_done.html'}),
    url(r'^resetpassword/$', 'django.contrib.auth.views.password_reset', {'password_reset_form': CustomPasswordResetForm,
                                                                          'template_name': 'registration/password_reset_form.html',
                                                                          'email_template_name':'registration/password_reset_email.html'}),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {'password_reset_form': CustomPasswordResetForm,
                                                                                                                 'template_name':'registration/password_reset_confirm.html'}),
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete', {'template_name':'registration/password_reset_complete.html'}),
        
)

# /api/student/4