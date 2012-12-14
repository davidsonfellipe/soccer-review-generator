from django.conf.urls.defaults import patterns, include, url
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^grappelli/', include('grappelli.urls')),
    # Examples:
    # url(r'^equipe/', include('equipe.urls')),
    # url(r'^$', 'cma.views.home', name='home'),
    # url(r'^cma/', include('cma.foo.urls')),
    url(r'^servico/(?P<jogo_id>\w{0,50})/$', 'esportes.views.get_game_text'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
