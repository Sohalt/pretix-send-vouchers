from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/send-vouchers/',
    views.SenderView.as_view(), name='send')
]
