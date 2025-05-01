from .models import Profile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .serializers import UserSerializer, RegistrationSerializer, LoginSerializer, UserLoginSerializer
from django.shortcuts import get_object_or_404
from .utils import generate_otp
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

class UserAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk=None):
        if pk:
            user = get_object_or_404(User, pk=pk)
            serializer = UserSerializer(user)
        else:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterAPIView(APIView):
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False 
            user.save()

            profile, created = Profile.objects.get_or_create(user=user)
            profile.otp = generate_otp()  
            profile.save()

            email_subject = 'Welcome To Our Platform!'
            email_body = render_to_string('welcome_email.html', {'username': user.username})

            email = EmailMultiAlternatives(email_subject, '', 'mdmamun340921@gmail.com', [user.email])
            email.attach_alternative(email_body, 'text/html')
            email.send()

            return Response({'detail': 'Check your email for confirmation'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPApiView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        user = get_object_or_404(User, email=email)

        otp_code = generate_otp()
        user.profile.otp = otp_code
        user.profile.save()

        send_mail(
            'Your OTP Code : ',
            f'Your New OTP Code Is : {otp_code}',
            'mdmamun340921@gmail.com',
            [email]
        )

        return Response({'Message' : 'OTP Has Been Resent To Your Email'}, status=status.HTTP_200_OK)

class VerifyOTPApiView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp = request.data.get('otp')

        user = get_object_or_404(User, email=email)
        profile = user.profile

        if profile.otp == otp:
            user.is_active = True
            user.save(update_fields=['is_active']) 
            profile.otp = None
            profile.save(update_fields=['otp']) 
            return Response({'Message' : 'Account Activate Successfully'}, status=status.HTTP_200_OK)
        return Response({'Error' : 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                serializer = UserLoginSerializer({
                    'username': user.username
                })
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            logout(request)
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)