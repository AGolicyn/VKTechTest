from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import (
    FriendRequest,
    Friendship,
    FriendStatus,
    CustomUser,
    MyAuthentication,
)
from .serializers import (
    UserSerializer,
    FriendRequestSerializer,
    FriendshipSerializer,
    FriendStatusSerializer,
)


@api_view(["POST"])
def registration_view(request):
    """
    Creating new user
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([MyAuthentication])
@permission_classes([IsAuthenticated])
def send_friend_request_view(request, username):
    """
    Send a friend request and accept friendship if there is an incoming request
    """
    from_user = request.user
    to_user = get_object_or_404(
        CustomUser.objects.exclude(id=from_user.id), username=username
    )

    if Friendship.objects.filter(
        Q(user1=from_user, user2=to_user) | Q(user1=to_user, user2=from_user)
    ).exists():
        return Response(
            {"error": "Users are already friends."}, status=status.HTTP_400_BAD_REQUEST
        )

    if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
        return Response(
            {"error": "Friend request already sent."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    friend_request = FriendRequest.objects.filter(from_user=to_user, to_user=from_user)
    if friend_request.exists():
        friendship = Friendship(user1=from_user, user2=to_user)
        friendship.save()
        friend_request.delete()
        serializer = FriendshipSerializer(friendship)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    friend_request = FriendRequest(from_user=from_user, to_user=to_user)
    friend_request.save()
    serializer = FriendRequestSerializer(friend_request)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@authentication_classes([MyAuthentication])
@permission_classes([IsAuthenticated])
def accept_friend_request_view(request, request_id):
    """
    Accept friend request
    """
    friend_request = get_object_or_404(
        FriendRequest, id=request_id, to_user=request.user
    )

    if Friendship.objects.filter(
        Q(user1=friend_request.from_user, user2=request.user)
        | Q(user1=request.user, user2=friend_request.from_user)
    ).exists():
        return Response(
            {"error": "Users are already friends."}, status=status.HTTP_400_BAD_REQUEST
        )

    friendship = Friendship(user1=friend_request.from_user, user2=request.user)
    friendship.save()
    friend_request.delete()
    serializer = FriendshipSerializer(friendship)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@authentication_classes([MyAuthentication])
@permission_classes([IsAuthenticated])
def reject_friend_request_view(request, request_id):
    """
    Reject friend request
    """
    friend_request = get_object_or_404(
        FriendRequest, id=request_id, to_user=request.user
    )
    friend_request.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@authentication_classes([MyAuthentication])
@permission_classes([IsAuthenticated])
def friend_requests_view(request):
    """
    View a list of incoming and outgoing requests
    """
    friend_requests_sent = FriendRequest.objects.filter(from_user=request.user)
    friend_requests_received = FriendRequest.objects.filter(to_user=request.user)
    serializer_sent = FriendRequestSerializer(friend_requests_sent, many=True)
    serializer_received = FriendRequestSerializer(friend_requests_received, many=True)
    return Response(
        {"sent": serializer_sent.data, "received": serializer_received.data}
    )


@api_view(["GET"])
@authentication_classes([MyAuthentication])
@permission_classes([IsAuthenticated])
def friends_view(request):
    """
    View a list of your friends
    """
    friendships = Friendship.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).select_related("user1", "user2")
    friend_ids = set()
    for friendship in friendships:
        if friendship.user1 != request.user:
            friend_ids.add(friendship.user1.id)
        if friendship.user2 != request.user:
            friend_ids.add(friendship.user2.id)
    friends = CustomUser.objects.filter(id__in=friend_ids)
    serializer = UserSerializer(friends, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([MyAuthentication])
@permission_classes([IsAuthenticated])
def friend_status_view(request, username):
    """
    Get friend status with some other user
    """
    user = get_object_or_404(CustomUser, username=username)

    if Friendship.objects.filter(
        Q(user1=request.user, user2=user) | Q(user1=user, user2=request.user)
    ).exists():
        serializer = FriendStatusSerializer({"status": FriendStatus.FRIENDS})
    elif FriendRequest.objects.filter(from_user=request.user, to_user=user).exists():
        serializer = FriendStatusSerializer({"status": FriendStatus.OUTGOING_REQUEST})
    elif FriendRequest.objects.filter(from_user=user, to_user=request.user).exists():
        serializer = FriendStatusSerializer({"status": FriendStatus.INCOMING_REQUEST})
    else:
        serializer = FriendStatusSerializer({"status": FriendStatus.NO_REQUEST})

    return Response(serializer.data)


@api_view(["DELETE"])
@authentication_classes([MyAuthentication])
@permission_classes([IsAuthenticated])
def remove_friend_view(request, username):
    """
    Remove user from your friends
    """
    user = get_object_or_404(CustomUser, username=username)
    friendship = Friendship.objects.filter(
        Q(user1=request.user, user2=user) | Q(user1=user, user2=request.user)
    )
    if not friendship.exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    friendship.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
