from django.conf.urls import url

from . import views

app_name = 'subscriptions'


urlpatterns = [
    url(r'^$', views.Subscribe.as_view(), name='subscribe'),
    url(r'^activate$', views.ActivateSubscription.as_view(), name='activate'),
    url(r'^deactivate$', views.DeactivateSubscription.as_view(), name='deactivate'),
]
