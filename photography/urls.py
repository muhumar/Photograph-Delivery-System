from django.contrib.auth import views as auth_views
from account import views as Account_View
from main import views as Main_View
from django.conf.urls.static import static
from django.conf.urls import url,include
from django.contrib import admin
from django.conf import settings

urlpatterns = [
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    url(r'^admin/', admin.site.urls),

    url(r'^booking/', include('booking.urls')),
    # url(r'^checkout/', Main_View.checkout, name='checkout'),
    url(r'^', include('main.urls', namespace="main")),

    # url(r'^contact/$', Main_View.email, name='email'),

    url(r'^profile/(?P<username>[^\.]+)', Account_View.profile, name='profile'),

    url(r'^change/password/$', Account_View.change_password, name='change_password'),
    url(r'^login/$', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'login'}, name='logout'),
    url(r'^account_activation_sent/$', Account_View.account_activation_sent, name='account_activation_sent'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        Account_View.activate, name='activate'),
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)