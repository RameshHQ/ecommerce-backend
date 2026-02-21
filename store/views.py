from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.utils.encoding import smart_bytes, smart_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage

from .models import Product, Cart, Order
from .serializers import (
    ProductSerializer,
    CartSerializer,
    OrderSerializer,
    PasswordResetSerializer,
    SetNewPasswordSerializer
)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            return Cart.objects.filter(user=user)

        session_key = self.request.session.session_key
        if not session_key:
            self.request.session.create()
            session_key = self.request.session.session_key

        return Cart.objects.filter(session_key=session_key)

    def create(self, request, *args, **kwargs):
        product_id = request.data.get("product")
        quantity = int(request.data.get("quantity", 1))

        if not product_id:
            return Response({"error": "Product is required"}, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        if request.user.is_authenticated:
            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={"quantity": quantity}
            )
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key

            cart_item, created = Cart.objects.get_or_create(
                session_key=session_key,
                product=product,
                defaults={"quantity": quantity}
            )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartSerializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=200)



class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)



class RegisterView(APIView):
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not email or not password:
            return Response({"error": "All fields are required"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=400)

        User.objects.create_user(username=username, email=email, password=password)
        return Response({"message": "User registered successfully"}, status=201)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            return Response({"error": "Email or password is incorrect"}, status=401)

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "username": user.username
        })




class RequestPasswordResetEmail(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        reset_link = None

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)

            reset_link = f"https://ecommerce-frontend-virid-eight-33.vercel.app/reset-password/{uidb64}/{token}/"

            EmailMessage(
                subject="Password Reset",
                body=f"Reset your password:\n{reset_link}",
                to=[user.email]
            ).send()

        return Response({
            "success": True,
            "message": "If this email is registered, a reset link has been sent.",
            "reset_link": reset_link  
        }, status=200)


class PasswordTokenCheckAPI(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = smart_str(urlsafe_base64_decode(uidb64))
            User.objects.get(id=uid)
            return Response({"success": True}, status=200)
        except Exception:
            return Response({"error": "Invalid link"}, status=400)


class SetNewPasswordAPIView(APIView):
    def patch(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "success": True,
            "message": "Password reset successful"
        }, status=200)