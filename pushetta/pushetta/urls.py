from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

from django.conf import settings

urlpatterns = patterns('',
                       url(r'^', include('www.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^api/', include('api.urls')),
)

if settings.ENVIRONMENT == "dev":
    urlpatterns += patterns('',
                            (r'^static/(?P<path>.*)$', 'django.views.static.serve',
                             {'document_root': settings.STATIC_ROOT}),
                            (r'^uploads/(?P<path>.*)$', 'django.views.static.serve',
                             {'document_root': settings.MEDIA_ROOT}),
    )