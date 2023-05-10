from django.urls import include, path
from friends.social import views

from .yasg import urlpatterns as doc_urls

urlpatterns = [
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("registration/", views.registration_view, name="registration"),
    path(
        "friendship/<int:request_id>/accept/",
        views.accept_friend_request_view,
        name="accept_friend_request",
    ),
    path(
        "friendship/<int:request_id>/reject/",
        views.reject_friend_request_view,
        name="reject_friend_request",
    ),
    path(
        "friend/<str:username>/request/",
        views.send_friend_request_view,
        name="send_friend_request",
    ),
    path(
        "friend/<str:username>/status/", views.friend_status_view, name="friend_status"
    ),
    path(
        "friend/<str:username>/remove/", views.remove_friend_view, name="remove_friend"
    ),
    path("friend/waiting/", views.friend_requests_view, name="friend_requests"),
    path("friend/", views.friends_view, name="friends"),
]

urlpatterns += doc_urls
