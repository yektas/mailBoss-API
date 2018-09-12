from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from api.authentication import CsrfExemptSessionAuthentication
from api.serializers import EmailSerializer, UserSerializer, UserLoginSerializer
from main.models import Email


class UsersFeed(GenericAPIView):
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        responseData = []

        users = self.get_queryset().exclude(pk=pk)
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


class CheckUserView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_email = request.data["email"]
        try:
            user_obj = User.objects.get(email=user_email)
            if user_obj is not None:
                return Response(status=HTTP_200_OK)
            else:
                return Response(status=HTTP_404_NOT_FOUND)
        except:
            return Response(status=HTTP_400_BAD_REQUEST)



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


class EmailCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        data = request.data["mail"]
        from_user_id = data["from_user"]
        to_email = data["to_email"]
        subject = data["subject"]
        content = data["content"]
        try:
            from_user = User.objects.get(id=from_user_id)
            to_user = User.objects.get(email=to_email)
            created = Email.objects.create(from_user=from_user, to_user=to_user, subject=subject, content=content)
            if created is not None:
                serializer = EmailSerializer(created)
                return Response(status=HTTP_200_OK)
            else:
                return Response(status=HTTP_400_BAD_REQUEST)
        except:
            return Response(status=HTTP_400_BAD_REQUEST)


class EmailReplyView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            email = Email.objects.get(pk=pk)
            return email
        except:
            return None

    def post(self, request, pk):
        email = self.get_object(pk=pk)
        replier = User.objects.get(id=email.to_user.id)
        content = request.data["data"]["content"]
        subject = request.data["data"]["subject"]
        reply_email = Email.objects.create(
            from_user=replier,
            to_user=email.from_user,
            subject=subject,
            content=content,
        )
        if (email.reply_mail is None):
            email.reply_mail = reply_email
            email.save()
            return Response(status=HTTP_200_OK)
        else:
            return Response(status=HTTP_400_BAD_REQUEST)


class EmailBetweenListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, from_user, to_user):
        from_user_id = int(from_user)
        to_user_id = int(to_user)
        try:
            emails = Email.objects.filter(
                Q(from_user_id=from_user_id, to_user_id=to_user_id) |
                Q(from_user_id=to_user_id, to_user=from_user_id)
            ).order_by("-timestamp").distinct()
            serializer = EmailSerializer(emails, many=True)
            return Response(serializer.data, status=HTTP_200_OK)
        except:
            return Response(status=HTTP_400_BAD_REQUEST)


class EmailMarkAsReadView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email_id = int(request.data["id"])
        try:
            email = Email.objects.get(id=email_id)
            email.read = True
            email.save()
            return Response(status=HTTP_200_OK)
        except:
            return Response(status=HTTP_400_BAD_REQUEST)
