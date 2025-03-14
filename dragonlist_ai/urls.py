"""
URL configuration for dragonlist_ai project.

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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from boards import urls as boards
from boards.views import (
    AuthViewSet, ListViewSet, CardViewSet, 
    LabelViewSet, ChecklistViewSet, ChecklistItemViewSet,
    AttachmentViewSet, CardLocationViewSet, UserViewSet  ,add_card_member, remove_card_member, add_card_dates, remove_card_dates
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('boards.urls')),
    # Auth endpoints
    path('api/auth/register/', AuthViewSet.as_view({'post': 'register'}), name='auth-register'),
    path('api/auth/login/', AuthViewSet.as_view({'post': 'login'}), name='auth-login'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
