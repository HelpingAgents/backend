from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, status
from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.conf import settings
from twilio.twiml.voice_response import VoiceResponse

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


@api_view(["POST"])
def logout(request):
    logout(request)
    return Response()


@api_view(["GET", "POST"])
@permission_classes([])
def enqueue_call(request):
    resp = VoiceResponse()
    resp.say("Hallo, dein Anruf wird weitergeleitet", language="de-DE")
    resp.enqueue(None, workflowSid=settings.TWILIO_WORKFLOW_SID)
    return HttpResponse(str(resp), content_type="application/xml")


@api_view(["GET", "POST"])
@permission_classes([])
def assignment(request):
    """ Task assignment """
    response = {
        "instruction": "dequeue",
        "post_work_activity_sid": settings.TWILIO_ACTIVITY_AVAILABLE_SID,
    }
    return Response(response)


@api_view(["POST"])
@permission_classes([])
def events(request):
    event_type = request.POST.get("EventType")
    workspace_sid = request.POST.get("WorkspaceSid")
    if event_type == "task.wrapup" and workspace_sid == settings.TWILIO_WORKSPACE_SID:
        task_sid = request.POST.get("TaskSid")
        serializers.client.taskrouter.workspaces(settings.TWILIO_WORKSPACE_SID).tasks(
            task_sid
        ).update(
            assignment_status="completed", reason="Call completed via Shoppingline"
        )
    return Response()
