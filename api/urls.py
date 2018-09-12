from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from api import views
from api.views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, base_name="user")

urlpatterns = [
    url(r'^user/emails/(?P<pk>\d+)/reply/', views.EmailReplyView.as_view()),
    url(r'^user/emails/(?P<from_user>\d+)/(?P<to_user>\d+)', views.EmailBetweenListView.as_view()),
    url(r'^user/emails/(?P<pk>\d+)', views.EmailListView.as_view()),
    url(r'^user/emails/', views.EmailCreateView.as_view()),
    url(r'^email/mark-as-read/', views.EmailMarkAsReadView.as_view()),
    url(r'^feed/users/(?P<pk>\d+)', views.UsersFeed.as_view()),
    url(r'^auth/create-user/', views.UserCreate.as_view()),
    url(r'^auth/login/', views.UserLogin.as_view()),

]
urlpatterns += router.urls
