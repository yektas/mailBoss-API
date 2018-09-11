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


class UsersFeed(GenericAPIView):
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
            responseJson = {
                "id": data["id"],
                "username": data["username"],
                "email": data["email"],
                "token": data["token"]
            }
            return Response(responseJson, status=HTTP_200_OK)
        return Response(status=HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()


class EmailListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            user = User.objects.get(pk=pk)
            emails = Email.objects.filter(
                Q(from_user=user) |
                Q(to_user=user)
            ).order_by("-timestamp").distinct()
            return emails
        except:
            return None

    def get(self, request, pk):
        emails = self.get_object(pk)
        serializer = EmailSerializer(emails, many=True)
        return Response(serializer.data)





class EmailViewSet(viewsets.ModelViewSet):
    # authentication_classes = [BasicAuthentication]
    #permission_classes = [IsAuthenticated]
    serializer_class = EmailSerializer
    queryset = Email.objects.all()
