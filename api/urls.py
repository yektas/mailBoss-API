from django.conf.urls import url

from api import views

urlpatterns = [
    url(r'^user/emails/mark-as-deleted/', views.EmailMarkAsDeletedView.as_view()),
    url(r'^user/emails/mark-as-read/', views.EmailMarkAsReadView.as_view()),
    url(r'^user/emails/replies/(?P<pk>\d+)', views.EmailPreviousRepliesView.as_view()),
    url(r'^user/emails/reply/', views.EmailReplyView.as_view()),
    url(r'^user/emails/(?P<sender_id>\d+)/(?P<receiver_id>\d+)', views.EmailBetweenListView.as_view()),
    url(r'^user/emails/(?P<pk>\d+)', views.EmailListView.as_view()),
    url(r'^email/send/', views.EmailCreateView.as_view()),
    url(r'^user/check-user/', views.CheckUserView.as_view()),
    url(r'^feed/users/(?P<pk>\d+)', views.UsersFeed.as_view()),
    url(r'^auth/create-user/', views.UserCreate.as_view()),
    url(r'^auth/login/', views.UserLogin.as_view()),
]
