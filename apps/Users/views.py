from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from apps.Users.models import FriendRequest, User
from apps.Users.serializer import (
    LoginSerializer, 
    UserSearchSerializer, 
    UserSerializer, 
    UserSignupSerializer,
    FriendRequestSerializer,
    UserNameUpdateSerializer,
)


User = get_user_model()

class UserSignupView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user_obj, created = User.objects.get_or_create(
                email=serializer.validated_data['email'],
                defaults=serializer.validated_data
            )
            if created:
                custom_data = {
                    "message": "User Registered Successfully",
                    "data": serializer.data
                }
                return Response(custom_data, status=status.HTTP_201_CREATED)
            else:
                custom_data = {
                    "message": "User already registered. Try logging in.",
                }
                return Response(custom_data, status=status.HTTP_200_OK)
        else:
            custom_data = {
                "message": serializer.errors,
            }
            return Response(custom_data, status=status.HTTP_400_BAD_REQUEST)



class UserLoginView(APIView):
    
    def get(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            try:
                data = serializer.validated_data
                custom_data = {
                    'message': 'User logged in successfully',
                    'data': data
                }
                return Response(custom_data, status=status.HTTP_200_OK)
            except AuthenticationFailed as e:
                custom_data = {
                    'message': str(e.detail)
                }
                return Response(custom_data, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserNameUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserNameUpdateSerializer

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            if user_id:
                try:
                    user_obj = User.objects.get(pk=user_id)
                except Http404:
                    return Response({"error": "User Not Found."}, status=status.HTTP_404_NOT_FOUND)
            else:
                try:
                    user_obj = User.objects.get(pk=request.user.id)
                except Http404:
                    return Response({"error": "User Not Found."}, status=status.HTTP_404_NOT_FOUND)

            if user_obj:
                user_obj.name = serializer.validated_data['name']
                user_obj.save()

                custom_data = {
                    "message": "User Name Updated Successfully.",
                }
                return Response(custom_data, status=status.HTTP_200_OK)


class UserSearchAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSearchSerializer
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.query_params)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            name = serializer.validated_data.get('name')

            queryset = User.objects.all()

            if email:
                queryset = queryset.filter(email__iexact=email)
            elif name:
                queryset = queryset.filter(name__icontains=name)
            else:
                custom_data = {"error": "Please provide either 'email' or 'name' as search parameter."}
                return Response(custom_data, status=status.HTTP_400_BAD_REQUEST)

            # Paginate the queryset
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            # Serialize paginated data
            serializer = UserSerializer(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        requested_user_id = request.user.id
        request_recived_user_id = request.data.get('request_recived_user_id')
        requested_user = get_object_or_404(User, pk=requested_user_id)
        
        try:
            request_recived_user = get_object_or_404(User, pk=request_recived_user_id)
        except Http404:
            return Response({"error": "Friend not found."}, status=status.HTTP_404_NOT_FOUND)

        if requested_user == request_recived_user:
            return Response({"error": "You cannot send Friend Request to Same User."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        if not FriendRequest.can_send_friend_request(requested_user):
            return Response({"error": "You cannot send more than 3 friend requests within a minute."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        if FriendRequest.check_already_request_send(requested_user, request_recived_user):
            return Response({"message": "Already have pending request."},
                            status=status.HTTP_200_OK)

        FriendRequest.objects.create(requested_user=requested_user, 
                                    request_recived_user=request_recived_user
                                    )
        return Response({"message": "Friend request sent successfully."},
                        status=status.HTTP_201_CREATED)


class AcceptFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request_id = request.data.get('request_id')
        try:
            friend_request = get_object_or_404(FriendRequest, pk=request_id, status=1)
        except Http404:
            return Response({"error": "This friend request is no longer pending."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        if friend_request.requested_user != request.user:
            return Response({"error": "You do not have permission to accept this friend request."},
                            status=status.HTTP_403_FORBIDDEN)

        friend_request.status = 2
        friend_request.save()

        return Response({"message": "Friend request accepted successfully."},
                        status=status.HTTP_200_OK)


class RejectFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request_id = request.data.get('request_id')

        try:
            friend_request = get_object_or_404(FriendRequest, pk=request_id, status=1)
        except Http404:
            return Response({"error": "This friend request is no longer pending."},
                            status=status.HTTP_400_BAD_REQUEST)

        if friend_request.requested_user != request.user:
            return Response({"error": "You do not have permission to accept this friend request."},
                            status=status.HTTP_403_FORBIDDEN)

        friend_request.status = 3
        friend_request.save()

        return Response({"message": "Friend request rejected successfully."},
                        status=status.HTTP_200_OK)


class ListFriends(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        request_user = get_object_or_404(User, pk=user.id)

        queryset = [friends.request_recived_user for friends in FriendRequest.objects.filter(requested_user=request_user, status=2)]
        serializer = UserSerializer(queryset, many=True)
        custom_data = {
            "message": "Friend request rejected successfully.",
            "data": serializer.data
        }
        return Response(custom_data, status=status.HTTP_200_OK)


class ListPendingFriendsRequest(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        request_user = get_object_or_404(User, pk=user.id)

        queryset = FriendRequest.objects.filter(requested_user=request_user, status=1)
        serializer = FriendRequestSerializer(queryset, many=True)
        custom_data = {
            "message": "Listed Pending Friends Requests.",
            "data": serializer.data
        }
        return Response(custom_data, status=status.HTTP_200_OK)






