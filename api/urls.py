from django.urls import path, include
from rest_framework import routers

from .views import (
    IncomingFriendRequestListView,
    OutgoingFriendRequestListView,
    FriendList,
    FriendRequestCreateAPIView,
    delete_friend,
    get_friendship_status,
    FriendRequestDetailView,
    UserViewSet
)


router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="user")


urlpatterns = [
    path("friends-list/", FriendList.as_view(), name="friends-list"),
    # path('requests/', FriendRequestUpdateRetrieveView.as_view(), name="see_answer_request"),
    path(
        "requests/<int:sender_id>/",
        FriendRequestDetailView.as_view(),
        name="incoming-friend-request",
    ),
    path("delete-friend/<int:friend_id>/", delete_friend, name="delete_friend"),
    path(
        "friends/status/<int:user_id>/", get_friendship_status, name="friendship_status"
    ),
    path("", include(router.urls)),
    path(
        "send-request/<int:receiver_id>",
        FriendRequestCreateAPIView.as_view(),
        name="send-request",
    ),
    path(
        "requests/incoming/",
        IncomingFriendRequestListView.as_view(),
        name="incoming-requests-list",
    ),
    path(
        "requests/outgoing/",
        OutgoingFriendRequestListView.as_view(),
        name="outgoing-requests-list",
    ),
]
