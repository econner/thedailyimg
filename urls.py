from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
import os

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),
    
    (r'^$', "core.views.index"),
    
    (r'^login/?$', "core.views.login"),
    (r'^logout/?$', "core.views.logout"),
    (r'^register/?$', "core.views.register"),
    
    (r'^submit/?$', "core.views.submit"),
    (r'^list/(?P<category>\d+)/?$', "core.views.list"),
    url(r'^im/(?P<image_id>\d+)/?$', "core.views.image", name="image"),
    
    (r'^manual/?$', "core.views.manual"),
    
    (r'^ajax/vote/?$', "core.views.vote"),
    (r'^ajax/page/?$', "core.views.page"),
    
    (r'^facebook/', include("facebook.urls")),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': os.path.dirname(settings.PROJECT_ROOT)}),
    )