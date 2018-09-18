from django.contrib.auth.models import User
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from api.authentication import CsrfExemptSessionAuthentication
from api.serializers import UserSerializer, UserLoginSerializer, MailSerializer, MessageSerializer, StatusSerializer, \
    UserCreateSerializer
from main.models import Message, Message_Recipient, Status


class UsersFeed(GenericAPIView):
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        users = self.get_queryset().exclude(pk=pk)

        responseData = []
        for user in users:
            userData = UserSerializer(user).data
            try:
                lastSentMail = Message.objects.filter(sender=user).order_by("-timestamp").first()
                lastReceivedMail = Message_Recipient.objects.filter(receiver=user).order_by(
                    "-message__timestamp").first()
                if lastReceivedMail.message.timestamp > lastSentMail.timestamp:
                    lastMail = lastReceivedMail
                else:
                    lastMail = Message_Recipient.objects.get(message=lastSentMail)

                mailData = {
                    "last_email": MailSerializer(lastMail).data,
                }
            except:
                data = {**userData, "last_email": "", "receiver": ""}
                responseData.append(data)
                continue
            responseData.append({**userData, **mailData})
        return Response(responseData)
class UserCreate(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
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
        user_email = request.data["email"].strip()
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

    def get(self, request, pk):
        user = User.objects.get(pk=pk)

        sent_messages = Message.objects.filter(sender=user, parent=None)
        received_messages = Message_Recipient.objects.filter(receiver=user).select_related("message").filter(
            message__parent=None)

        sent_mails = Message_Recipient.objects.filter(message__in=sent_messages)

        allMails = (sent_mails | received_messages).order_by("-message__timestamp")

        data = []

        for mail in allMails:
            mail_status = Status.objects.get(user=user, message=mail.message)
            lastReply = mail.message.lastReply
            if not mail_status.isDeleted:
                if lastReply is not None:
                    data.append({
                        "parentMail": MailSerializer(mail).data,
                        "lastReply": MailSerializer(lastReply).data,
                        "status": StatusSerializer(mail_status).data
                    })
                else:
                    data.append({
                        "parentMail": MailSerializer(mail).data,
                        "lastReply": MailSerializer(mail).data,
                        "status": StatusSerializer(mail_status).data
                    })

        data.sort(key=lambda d: d['lastReply']['message']['timestamp'], reverse=True)

        return Response(data, status=HTTP_200_OK)

class EmailPreviousRepliesView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

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
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data["mail"]
        sender_id = data["sender_id"]
        receiver_email = data["receiver_email"]
        subject = data["subject"]
        body = data["body"]

        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(email=receiver_email)


        newMessage = Message.objects.create(sender=sender, subject=subject, body=body, parent=None)

        if sender.id == receiver.id:
            Status.objects.create(user=sender, isRead=False, message=newMessage)
        else:
            Status.objects.create(user=sender, isRead=True, message=newMessage)
            Status.objects.create(user=receiver, message=newMessage)
        Message_Recipient.objects.create(receiver=receiver, message=newMessage)

        return Response(status=HTTP_200_OK)

class EmailReplyView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

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
        current_status = Status.objects.filter(message=current_mail)
        for status in current_status:
            if status.user.id == sender.id:
                status.isRead = True
            if status.user.id == receiver.id:
                status.isDeleted = False
                status.isRead = False
            status.save()
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

    def get(self, request, sender_id, receiver_id):

        sender = User.objects.get(pk=sender_id)
        receiver = User.objects.get(pk=receiver_id)

        parent1 = Message.objects.filter(sender=sender, parent=None)

        mails = []
        for parent in parent1:
            try:
                status = Status.objects.get(user=sender, message=parent.id)
                if not status.isDeleted:
                    if parent.receiver == receiver:
                        mails.append(MessageSerializer(parent).data)
            except:
                continue
        parent2 = Message.objects.filter(sender=receiver, parent=None)
        for parent in parent2:
            try:
                status = Status.objects.get(user=sender, message=parent.id)
                if not status.isDeleted:
                    if parent.receiver == sender:
                        mails.append(MessageSerializer(parent).data)
            except:
                continue

        mails.sort(key=lambda d: d['timestamp'], reverse=True)

        return Response(mails, status=HTTP_200_OK)
class EmailMarkAsReadView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data["mail"]
        current_user_id = request.data["current_user"]
        try:
            user = User.objects.get(pk=current_user_id)

            parentMail = Message.objects.get(pk=data["parentMail"]["message"]["id"])
            status = Status.objects.get(user=user, message=parentMail)
            status.isRead = True
            status.save()
            return Response(status=HTTP_200_OK)
        except:
            return Response(status=HTTP_400_BAD_REQUEST)


class EmailMarkAsDeletedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        mail = request.data["mail"]
        current_user_id = request.data["current_user"]
        try:
            user = User.objects.get(pk=current_user_id)
            parentMail = Message.objects.get(pk=mail["parentMail"]["message"]["id"])
            status = Status.objects.get(user=user, message=parentMail)
            status.isDeleted = True
            status.isRead = True
            status.save()
            return Response(status=HTTP_200_OK)
        except:
            return Response(status=HTTP_400_BAD_REQUEST)
