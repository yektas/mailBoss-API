from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import EmailSerializer
from main.models import Email


class UserList(APIView):
    authentication_classes = [BasicAuthentication]

    # permission_classes = [IsAuthenticated]

    def get(self, request):
        data = []
        users = User.objects.all()
        for user in users:
            mail = Email.objects.filter(
                Q(from_user=user) |
                Q(to_user=user)
            ).order_by("-timestamp")[0]
            serializer = EmailSerializer(mail)
            data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "last_email": serializer.data,
                "date": mail.timestamp.strftime("%d %b")
            })
        return Response(data)


class EmailViewSet(viewsets.ModelViewSet):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = EmailSerializer
    queryset = Email.objects.all()
