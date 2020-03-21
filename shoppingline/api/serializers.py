from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework import serializers
from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from shoppingline.users.models import User

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

class LoginRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        try:
            client.verify \
            .services(settings.TWILIO_SERVICE_ID) \
            .verifications \
            .create(to=phone_number, channel='sms')
        except TwilioRestException as err:
            raise exceptions.ValidationError({
                "phone_number": err.msg
            })
        except Exception as err:
            raise exceptions.ValidationError(err)
        return attrs



class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField()

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        code = attrs.get("code")
        try:
            verification_check = client.verify \
                .services(settings.TWILIO_SERVICE_ID) \
                .verification_checks.create(to=phone_number, code=code)
        except TwilioRestException as err:
            raise exceptions.ValidationError({
                "phone_number": "Verification expired"
            })
        if verification_check.status != "approved":
            raise exceptions.ValidationError({
                "phone_number": "Internal API error."
            })

        user = User.objects.filter(phone_number__iexact=phone_number).first()

        if not user:
            user = User.objects.create(phone_number=phone_number)


        if not user.is_active:
            raise exceptions.ValidationError({
                "phone_number": "Account is not activated."
            })

        attrs["user"] = user
        return attrs



class UserAuthInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "phone_number",
            "first_name",
            "last_name",
            "accepting_calls",
        )

class ProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    accepting_calls = serializers.BooleanField()

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "accepting_calls",
        )