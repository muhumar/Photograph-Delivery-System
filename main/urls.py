from django.conf.urls import url,include
from . import views


urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^about', views.about, name='about'),
    url(r'^privacy_policy', views.privacy, name='privacy'),
    url(r'^portfolio', views.portfolio, name='portfolio'),
    # url(r'^payment', views.payment, name='payment'),
   url(r'^payment/$', views.payment_method_view, name='payment-method'),
    url(r'^payment/create/$', views.payment_method_createview, name='payment-method-create'),
    # url(r'^contact', views.contact, name='contact'),
    url(r'^paypal-home', views.paypal_home, name='paypal_home'),
    url(r'^paypal-return', views.paypal_return, name='paypal_return'),
    url(r'^paypal-cancel', views.paypal_cancel, name='paypal_cancel'),
    url(r'^a-very-hard-to-guess-url',include('paypal.standard.ipn.urls')),
    url(r'^category/(?P<slug>[^\.]+)', views.category, name='category'),
]
