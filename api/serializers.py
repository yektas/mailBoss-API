from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, Field
from rest_framework.serializers import ModelSerializer

from main.models import Email


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


class TimestampField(Field):
    def to_representation(self, obj):
        obj = obj.strftime("%d %B %Y %H:%M")
        return obj


class EmailSerializer(ModelSerializer):
    from_user = UserSerializer()
    to_user = UserSerializer()
    timestamp = TimestampField()

    class Meta:
        model = Email
        fields = [
            "id",
            "from_user",
            "to_user",
            "subject",
            "timestamp",
            "reply_mail",
            "read",
            "content"
        ]


class EmailCreateSerializer(ModelSerializer):
    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)
    subject = CharField()
    content = CharField()

    class Meta:
        model = Email
        fields = "__all__"
