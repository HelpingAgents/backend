from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, status
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt

from shoppingline.users.models import User
from shoppingline.api import serializers

class LoginRequestView(generics.CreateAPIView):
    serializer_class = serializers.LoginRequestSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response()

class LoginView(generics.CreateAPIView):
    serializer_class = serializers.LoginSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return Response()


class AuthInfoView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserAuthInfoSerializer

    def get_object(self):
        return self.request.user


class ProfileUpdateView(generics.UpdateAPIView):
    serializer_class = serializers.ProfileUpdateSerializer

    def get_object(self):
        return self.request.user

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ProfileUpdateView, self).dispatch(request, *args, **kwargs)

@api_view(["GET"])
def logout(request):
    logout(request)
    return Response()
