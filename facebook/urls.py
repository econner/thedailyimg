from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('facebook.views',
    url(r'^login/?$', 'login', name='facebook-login'),
    url(r'^callback/?$', 'callback', name='facebook-callback'),
)
