from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (CommentViewSet, ReviewViewSet)

router = SimpleRouter()
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet, basename='reviews')
# router.register(r'posts', PostViewSet, basename='posts')
# router.register(r'groups', GroupViewSet, basename='groups')

urlpatterns = [
    # path('v1/follow/', FollowListCreate.as_view()),
    # path('v1/', include('djoser.urls.jwt')),
    path('v1/', include(router.urls))
]
