from django.urls import path, include
from apps.Users.views import (
    UserSignupView, 
    UserSearchAPIView, 
    UserLoginView, 
    SendFriendRequestView, 
    AcceptFriendRequestView,
    RejectFriendRequestView,
    ListFriends,
    ListPendingFriendsRequest,
    UserNameUpdateView,
)
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('register', UserSignupView, basename='User')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('user-name-update/', UserNameUpdateView.as_view(), name='user-name-update'),
    path('search/', UserSearchAPIView.as_view(), name='user-search'),
    path('send-friends-requests/', SendFriendRequestView.as_view(), name='send-user-friends-requests'),
    path('accept-friend-request/', AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    path('reject-friend-request/', RejectFriendRequestView.as_view(), name='reject-friend-request'),
    path('list-friends/', ListFriends.as_view(), name='list-friends'),
    path('list-pending-rquests/', ListPendingFriendsRequest.as_view(), name='list-pending-rquests'),
]
