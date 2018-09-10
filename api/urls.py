from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from api import views
from api.views import EmailViewSet

router = DefaultRouter()
router.register(r'emails', EmailViewSet, base_name='email')

urlpatterns = [
    url(r'users/', views.UserList.as_view()),
    url(r'auth/create-user/', views.UserCreate.as_view()),
    url(r'auth/login/', views.UserLogin.as_view())
]
