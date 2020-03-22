import json

from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Group
from django.core import exceptions
from rest_framework import serializers
from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import phonenumbers
from shoppingline.users.models import User

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


class LoginRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        try:
            parsed_phone_number = phonenumbers.parse(phone_number)
            if parsed_phone_number.country_code != 49:
                raise exceptions.ValidationError(
                    {
                        "phone_number": "Ungültige Ländervorwahl, nur Deutschland wird aktuell unterstützt."
                    }
                )
        except phonenumbers.phonenumberutil.NumberParseException:
            raise exceptions.ValidationError(
                {"phone_number": "Ungültige Telefonnummer"}
            )
        except Exception as ex:
            raise ex
        try:
            client.verify.services(settings.TWILIO_SERVICE_ID).verifications.create(
                to=phone_number, channel="sms"
            )
        except TwilioRestException as err:
            raise exceptions.ValidationError({"phone_number": err.msg})
        except Exception as err:
            raise exceptions.ValidationError(err)
        return attrs


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField()
    name = serializers.CharField()

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        code = attrs.get("code")
        name = attrs.get("name")
        try:
            parsed_phone_number = phonenumbers.parse(phone_number)
        except phonenumbers.phonenumberutil.NumberParseException:
            raise exceptions.ValidationError(
                {"phone_number": "Ungültige Telefonnummer"}
            )
        try:
            verification_check = client.verify.services(
                settings.TWILIO_SERVICE_ID
            ).verification_checks.create(to=phone_number, code=code)
        except TwilioRestException as err:
            raise exceptions.ValidationError({"phone_number": "Verification expired"})
        if verification_check.status != "approved":
            raise exceptions.ValidationError({"phone_number": "Internal API error."})

        user = User.objects.filter(phone_number__iexact=phone_number).first()

        if not user:
            worker = client.taskrouter.workspaces(
                settings.TWILIO_WORKSPACE_SID
            ).workers.create(
                friendly_name=name,
                attributes=json.dumps(
                    {"contact_uri": phone_number, "products": ["ProgrammableSMS"]}
                ),
            )

            user = User.objects.create(
                phone_number=phone_number, twilio_worker_sid=worker.sid, name=name,
            )

        if not user.is_active:
            raise exceptions.ValidationError(
                {"phone_number": "Account is not activated."}
            )

        attrs["user"] = user
        return attrs


class UserAuthInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "phone_number",
            "name",
            "accepting_calls",
        )


class ProfileUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    accepting_calls = serializers.BooleanField(required=False)

    def update(self, instance, validated_data):
        if "name" in validated_data:
            instance.name = validated_data.get("name")
        if "accepting_calls" in validated_data:
            previous_accepting_calls = instance.accepting_calls
            instance.accepting_calls = validated_data.get("accepting_calls")
            worker = (
                client.taskrouter.workspaces(settings.TWILIO_WORKSPACE_SID)
                .workers(instance.twilio_worker_sid)
                .fetch()
            )

            new_activity_sid = settings.TWILIO_ACTIVITY_OFFLINE_SID
            if previous_accepting_calls is False and instance.accepting_calls is True:
                new_activity_sid = settings.TWILIO_ACTIVITY_AVAILABLE_SID

            worker = (
                client.taskrouter.workspaces(settings.TWILIO_WORKSPACE_SID)
                .workers(instance.twilio_worker_sid)
                .update(activity_sid=new_activity_sid)
            )

        instance.save(update_fields=["name", "accepting_calls"])
        return instance

    class Meta:
        model = User
        fields = (
            "name",
            "accepting_calls",
        )
