"""
URL configuration for xdccDownloadManager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from irc_xdcc_manager import views
from rest_framework.routers import DefaultRouter, SimpleRouter

apiRouter = DefaultRouter()

apiRouter.register('irc_connections', views.IRCConnectionViewSet)
apiRouter.register('irc_channels', views.IRCChannelViewSet)
apiRouter.register('xdcc_offers', views.XDCCOfferViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.MainPageView.as_view(), name='home'),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(apiRouter.urls)),
    path('api/irc_running_connections', views.RunningIRCConnectionsAPI.as_view(), name='irc_running_connections'),
]

if settings.LOCAL_DEVELOPMENT:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)