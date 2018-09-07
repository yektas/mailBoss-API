from rest_framework.routers import DefaultRouter

from api.views import UserViewSet, EmailViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, base_name='user')
router.register(r'emails', EmailViewSet, base_name='email')

urlpatterns = router.urls