from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from api import views
from api.views import EmailViewSet, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, base_name="user")
router.register(r'emails', EmailViewSet, base_name='email')

urlpatterns = [


    url(r'^feed/users', views.UserList.as_view()),
    url(r'^auth/create-user/', views.UserCreate.as_view()),
    url(r'^auth/login/', views.UserLogin.as_view()),

]
urlpatterns += router.urls
