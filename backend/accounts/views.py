from django.middleware.csrf import get_token
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MemberInterest, User
from .permissions import IsAdmin
from .serializers import (
    AdminUserSerializer, LoginSerializer, MemberInterestSerializer,
    RegisterSerializer, UserSerializer,
)


class CsrfInitView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'csrfToken': get_token(request)})


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {'user': UserSerializer(user).data, 'token': token.key},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'user': UserSerializer(user).data, 'token': token.key})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MemberInterestListView(generics.ListCreateAPIView):
    serializer_class = MemberInterestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MemberInterest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MemberInterestDeleteView(generics.DestroyAPIView):
    serializer_class = MemberInterestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MemberInterest.objects.filter(user=self.request.user)


class AdminUserListView(generics.ListAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]
    queryset = User.objects.all()
    search_fields = ['email', 'first_name', 'last_name']
    filterset_fields = ['role', 'is_suspended']


class AdminUserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]
    queryset = User.objects.all()

    def patch(self, request, *args, **kwargs):
        """Role management + suspension, restricted to admins server-side."""
        instance = self.get_object()
        if instance == request.user and 'role' in request.data:
            return Response({'detail': 'Cannot change your own role.'}, status=400)
        return super().patch(request, *args, **kwargs)
