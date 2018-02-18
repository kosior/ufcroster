from django.conf.urls import url

from . import views

app_name = 'fighters'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<country_code>[\w]{2})/$', views.UpcomingFightsByCountry.as_view(), name='upcoming-by-country'),
    url(r'^(?P<country_code>[\w]{2})/fighters$', views.FightersByCountry.as_view(), name='by-country'),
    url(r'^(?P<slug>[\w\-]+)/$', views.FighterDetail.as_view(), name='detail'),
]
