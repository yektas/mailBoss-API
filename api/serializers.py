from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, ReadOnlyField
from rest_framework.serializers import ModelSerializer

from main.models import Message, Message_Recipient


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password'
        ]
        extra_kwargs = {
            'password': {
                'write_only': True,
            }
        }

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            password=make_password(validated_data['password'])
        )
        user.save()
        return user


class UserLoginSerializer(ModelSerializer):
    username = CharField()
    password = CharField()

    class Meta:
        model = User
        fields = [
            "username",
            "password"
        ]
        extra_kwargs = {
            "password": {
                "write_only": True,
            }
        }

    def validate(self, data):
        username = data["username"]
        password = data["password"]
        user = User.objects.filter(username=username)
        if user.exists() and user.count() == 1:
            user_obj = user.first()
        else:
            raise ValidationError("Credentials are wrong")

        if user_obj:
            if not user_obj.check_password(password):
                raise ValidationError("Incorrect credentials")
        token, created = Token.objects.get_or_create(user=user_obj)
        data["token"] = token.key
        data["id"] = user_obj.id
        data["email"] = user_obj.email
        return data


class MessageSerializer(ModelSerializer):
    sender = UserSerializer()
    receiver = UserSerializer(ReadOnlyField())
    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            "subject",
            "body",
            "timestamp",
            "isRead",
            "isDeleted",
            "parent",
            "receiver"
        ]


class MailSerializer(ModelSerializer):
    message = MessageSerializer()
    receiver = UserSerializer()

    class Meta:
        model = Message_Recipient
        fields = [
            "id",
            "receiver",
            "message",
            "isRead",
            "isDeleted"
        ]
