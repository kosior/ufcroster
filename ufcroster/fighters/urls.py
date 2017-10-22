from django.conf.urls import url

from . import views

app_name = 'fighters'

urlpatterns = [
    url(r'^(?P<slug>[\w\-]+)/$', views.FighterDetail.as_view(), name='detail'),
]
