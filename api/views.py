from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from api.authentication import CsrfExemptSessionAuthentication
from api.serializers import EmailSerializer, UserSerializer, UserLoginSerializer
from main.models import Email


class UserList(GenericAPIView):
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):

        responseData = []

        users = self.get_queryset()
        for user in users:
            userData = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
            try:
                mail = Email.objects.filter(
                    Q(from_user=user) |
                    Q(to_user=user)
                ).order_by("-timestamp")[0]
                serializer = EmailSerializer(mail)
                mailData = {
                    "last_email": serializer.data,
                    "date": mail.timestamp.strftime("%d %b")
                }
            except:
                data = {**userData, "last_email": "", "date": ""}
                responseData.append(data)
                continue
            responseData.append({**userData, **mailData})
        return Response(responseData)


class UserCreate(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserLogin(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            return Response({"token": data["token"]}, status=HTTP_200_OK)
        return Response(status=HTTP_400_BAD_REQUEST)



class EmailViewSet(viewsets.ModelViewSet):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = EmailSerializer
    queryset = Email.objects.all()
