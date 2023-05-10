from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework import generics, status, viewsets
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, FriendRequest
from api.serializers import FriendRequestSerializer, FriendRequestUpdateSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class FriendList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        friends = user.friends.all()
        return friends

    def list(self, request):
        queryset = self.get_queryset()

        # Check if user has no friends
        if not queryset.exists():
            return Response({"Message": "User has no friends yet."})

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FriendRequestCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, receiver_id):
        receiver = get_object_or_404(User, id=receiver_id)

        if receiver == request.user:
            return Response(
                {"Error": "You cannot send a friend request to yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if a friend request from the authenticated user to the receiver already exists
        friend_request_exists = FriendRequest.objects.filter(
            sender=request.user, receiver=receiver
        ).exists()
        if friend_request_exists:
            return Response(
                {"Error": "A friend request from you to this user already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the receiver has already sent a friend request to the authenticated user
        incoming_req_exists = FriendRequest.objects.filter(
            sender=receiver, receiver=request.user
        ).exists()
        if incoming_req_exists:
            # Accept the existing friend request and create a new one
            existing_friend_request = FriendRequest.objects.get(
                sender=receiver, receiver=request.user
            )
            existing_friend_request.status = FriendRequest.ACCEPTED
            existing_friend_request.save()

            request_friend_request = FriendRequest(
                sender=request.user, receiver=receiver, status=FriendRequest.ACCEPTED
            )
            request_friend_request.save()

            request_user = request.user
            request_user.friends.add(receiver)
            request_user.save()

            receiver.friends.add(request_user)
            receiver.save()

            return Response(
                {
                    "Message": "Friend request already exists, both users are now friends."
                },
                status=status.HTTP_200_OK,
            )

        # Create a new friend request
        friend_request = FriendRequest(sender=request.user, receiver=receiver)
        friend_request.save()

        return Response(
            {"Message": "Friend request sent successfully."},
            status=status.HTTP_201_CREATED,
        )


class IncomingFriendRequestListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(
            receiver=self.request.user, status=FriendRequest.PENDING
        )

    def list(self, request):
        queryset = self.get_queryset()

        # Check if user has no friends
        if not queryset.exists():
            return Response({"message": "User has no incoming requests yet."})

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OutgoingFriendRequestListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(sender=self.request.user).exclude(
            status=FriendRequest.ACCEPTED
        )

    def list(self, request):
        queryset = self.get_queryset()

        # Check if user has no friends
        if not queryset.exists():
            return Response({"message": "User has no outgoing requests yet."})

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_friend(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)

    if friend == request.user:
        return Response(
            {"Error": "You cannot delete yourself from list of friends."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # check if there are both way requests
    incoming_req_exists = FriendRequest.objects.filter(
        sender=request.user, receiver=friend, status=FriendRequest.ACCEPTED
    ).exists()
    outgoing_req_exists = FriendRequest.objects.filter(
        sender=friend, receiver=request.user, status=FriendRequest.ACCEPTED
    ).exists()

    if incoming_req_exists and outgoing_req_exists:
        # update the incoming request status to rejected
        incoming_friend_request = FriendRequest.objects.get(
            sender=friend, receiver=request.user, status=FriendRequest.ACCEPTED
        )
        incoming_friend_request.status = FriendRequest.REJECTED
        incoming_friend_request.save()

        # delete the outgoing friend request
        outgoing_friend_request = FriendRequest.objects.get(
            sender=request.user, receiver=friend, status=FriendRequest.ACCEPTED
        )
        outgoing_friend_request.delete()

        # remove the friend from the authenticated user's friends list
        request_user = request.user
        request_user.friends.remove(friend)
        request_user.save()

        # remove authenticated user from another user's friends list
        friend.friends.remove(request_user)
        friend.save()

        return Response(
            {"Message": "Friend deleted successfully."}, status=status.HTTP_200_OK
        )
    elif outgoing_req_exists:
        # if users not friends, we are simply removing
        # outgoing friend request

        outgoing_friend_request = FriendRequest.objects.get(
            sender=request.user, receiver=friend, status=FriendRequest.ACCEPTED
        )
        outgoing_friend_request.delete()
        return Response(
            {"Message": "No incoming request. Friendship request cancelled"},
            status=status.HTTP_404_NOT_FOUND,
        )
    else:
        return Response(
            {"Error": "No existing friend relationship found."},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_friendship_status(request, user_id):
    user = request.user
    other_user = get_object_or_404(User, id=user_id)

    if other_user == user:
        return Response(
            {"Error": "Cannot check friendship status with yourself"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # check if there are requests in both ways
    incoming_request = FriendRequest.objects.filter(
        sender=other_user, receiver=user
    ).first()
    outgoing_request = FriendRequest.objects.filter(
        sender=user, receiver=other_user
    ).first()

    # check if users are friends
    if user in other_user.friends.all() and other_user in user.friends.all():
        return Response({"Status": "Friends"})

    # if they re not friends, check the requests
    elif incoming_request:
        return Response({"Status": "Incoming request"})
    elif outgoing_request:
        return Response({"Status": "Outgoing request"})
    else:
        return Response({"Status": "Not friends"})


class FriendRequestDetailView(APIView):
    def get(self, request, sender_id):
        friend_request = FriendRequest.objects.filter(
            sender__id=sender_id, receiver=request.user
        ).first()
        if friend_request:
            serializer = FriendRequestSerializer(friend_request)
            return Response(serializer.data)
        else:
            return Response(
                {"Error": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def patch(self, request, sender_id):
        serializer = FriendRequestUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data["action"]

        sender = get_object_or_404(User, id=sender_id)
        user = request.user

        try:
            friend_request = FriendRequest.objects.get(
                sender_id=sender_id, receiver=user
            )
        except FriendRequest.DoesNotExist:
            return Response(
                {"Error": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if action == "accept":
            new_status = FriendRequest.ACCEPTED
        elif action == "reject":
            new_status = FriendRequest.REJECTED
        else:
            return Response(
                {"Error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST
            )

        if new_status == friend_request.status:
            return Response(
                {"Message": f"Friend request status is already {action}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_status == FriendRequest.ACCEPTED:
            friend_request.status = FriendRequest.ACCEPTED
            friend_request.save()

            # add the users to each other's friends lists
            sender.friends.add(user)
            user.friends.add(sender)

            # create a reverse way friend request
            new_friend_request = FriendRequest(
                sender=user, receiver=sender, status=FriendRequest.ACCEPTED
            )
            new_friend_request.save()
        elif new_status == FriendRequest.REJECTED:
            if friend_request.status == FriendRequest.ACCEPTED:
                sender.friends.remove(user)
                user.friends.remove(sender)

                outgoing_request = FriendRequest.objects.get(
                    sender=user, receiver=sender
                )
                outgoing_request.delete()

            friend_request.status = FriendRequest.REJECTED
            friend_request.save()

        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data)
