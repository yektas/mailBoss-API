from django.contrib.auth.models import User
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from api.authentication import CsrfExemptSessionAuthentication
from api.serializers import UserSerializer, UserLoginSerializer, MailSerializer, MessageSerializer
from main.models import Message, Message_Recipient


class UsersFeed(GenericAPIView):
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    permission_classes = [IsAuthenticated]

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
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

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
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = User.objects.get(pk=pk)
        received_messages = Message_Recipient.objects.filter(receiver=user). \
            select_related("message"). \
            filter(message__parent=None)
        sent_messages = Message.objects.filter(sender=user, parent=None)

        sent_mails = Message_Recipient.objects.filter(message__in=sent_messages)
        allMails = (sent_mails | received_messages).order_by("-message__timestamp")
        serializer = MailSerializer(allMails, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
        # received_messages = Message_Recipient.objects.filter(receiver=user).select_related("message").filter(message__parent=None)
        # sent_messages = Message.objects.filter(sender=user, parent=None)
        #
        # receivedSerializer = MailSerializer(received_messages, many=True)
        # sentSerializer = MessageSerializer(sent_messages, many=True)
        #
        # response = {
        #     "sent_messages": sentSerializer.data,
        #     "received_messages": receivedSerializer.data
        # }
        # return Response(response, status=HTTP_200_OK)


class EmailPreviousRepliesView(APIView):

    def get(self, request, pk):
        try:
            replies = Message.objects.filter(parent__id=pk).order_by("timestamp")
            parentMail = Message.objects.get(pk=pk)
            serializer = MessageSerializer(replies, many=True)
            response_data = {
                "parent_mail": MessageSerializer(parentMail).data,
                "replies": serializer.data
            }
            return Response(response_data, status=HTTP_200_OK)
        except:
            return Response(status=HTTP_400_BAD_REQUEST)

class EmailCreateView(APIView):
    # authentication_classes = [TokenAuthentication]
    #permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data["mail"]
        sender_id = data["sender_id"]
        receiver_email = data["receiver_email"]
        subject = data["subject"]
        body = data["body"]

        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(email=receiver_email)

        newMessage = Message.objects.create(sender=sender, subject=subject, body=body, parent=None)
        Message_Recipient.objects.create(receiver=receiver, message=newMessage)

        return Response(status=HTTP_200_OK)

class EmailReplyView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data["data"]

        parent_id = data["parent_id"]
        sender_id = data["sender_id"]
        receiver_id = data["receiver_id"]
        subject = data["subject"]
        body = data["body"]

        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)

        current_mail = Message.objects.get(pk=parent_id)

        # Parent mail yoksa ( İlk atılan maile verilen cevap )
        if current_mail.parent is None:
            newMessage = Message.objects.create(sender=sender, subject=subject, body=body, parent=current_mail)

        # Parent mail varsa ( Yani daha önce mail geçmişi var )
        else:
            newMessage = Message.objects.create(sender=sender, subject=subject, body=body, parent=current_mail.parent)

        Message_Recipient.objects.create(receiver=receiver, message=newMessage)

        return Response(status=HTTP_200_OK)

class EmailBetweenListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class EmailMarkAsReadView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class EmailMarkAsDeletedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
