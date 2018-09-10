from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField

from main.models import Email


class UserSerializer(serializers.ModelSerializer):
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


class UserLoginSerializer(serializers.ModelSerializer):
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
        token, created = Token.objects.get_or_create(user=user)
        data["token"] = token.key
        return data

class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = '__all__'