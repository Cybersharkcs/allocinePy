from django.conf.urls import patterns, url
from allocine import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index')
)