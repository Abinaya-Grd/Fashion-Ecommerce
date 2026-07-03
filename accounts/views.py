from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
import logging

from .models import CustomUser, OTP, Address
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    ProfileSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    VerifyEmailSerializer,
    AddressSerializer,
)
from .utils import generate_otp
from .email_service import (
    send_verification_email,
    send_forgot_password_email,
    send_reset_password_success_email,
    send_welcome_email,
)

logger = logging.getLogger("ecommerce")


def success_response(message, data=None, status_code=status.HTTP_200_OK):
    return Response({
        "success": True,
        "message": message,
        "data": data
    }, status=status_code)


def error_response(message, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({
        "success": False,
        "message": message
    }, status=status_code)


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]

            if CustomUser.objects.filter(email=email).exists():
                logger.warning(f"Registration failed - email already exists: {email}")
                return error_response("Email already exists")

            user = serializer.save()
            otp_code = generate_otp()

            OTP.objects.create(
                user=user,
                otp=otp_code,
                otp_type="email_verification"
            )

            try:
                send_verification_email(user, otp_code)
            except Exception as e:
                logger.error(f"Verification email failed for {user.email}: {e}")

            logger.info(f"New user registered: {user.email}")

            return success_response(
                "User registered successfully. OTP sent to email.",
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "phone": user.phone,
                    "role": user.role,
                    "is_email_verified": user.is_email_verified
                },
                status.HTTP_201_CREATED
            )

        logger.warning(f"Registration validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            otp_code = serializer.validated_data["otp"]

            try:
                user = CustomUser.objects.get(email=email)
                otp_obj = OTP.objects.filter(
                    user=user,
                    otp=otp_code,
                    otp_type="email_verification",
                    is_used=False
                ).latest("created_at")
            except Exception:
                logger.warning(f"Email verification failed for: {email}")
                return error_response("Invalid OTP or email")

            if not otp_obj.is_valid():
                logger.warning(f"Email verification OTP expired or used for: {email}")
                return error_response("OTP expired or already used")

            otp_obj.is_used = True
            otp_obj.save()

            user.is_email_verified = True
            user.save()

            try:
                send_welcome_email(user)
            except Exception as e:
                logger.error(f"Welcome email failed for {user.email}: {e}")

            logger.info(f"Email verified successfully: {user.email}")
            return success_response("Email verified successfully")

        logger.warning(f"Email verification validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                logger.warning(f"Failed login attempt - email not found: {email}")
                return error_response("Invalid email or password")

            if not user.check_password(password):
                logger.warning(f"Failed login attempt - wrong password: {email}")
                return error_response("Invalid email or password")

            logger.info(f"User logged in successfully: {user.email}")

            refresh = RefreshToken.for_user(user)

            return success_response(
                "Login successful",
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "phone": user.phone,
                        "role": user.role,
                        "is_email_verified": user.is_email_verified
                    }
                }
            )

        logger.warning(f"Login validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return success_response("Profile fetched successfully", serializer.data)

    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            logger.info(f"Profile updated: {request.user.email}")
            return success_response("Profile updated successfully", serializer.data)

        logger.warning(f"Profile update failed for {request.user.email}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user

            if not user.check_password(serializer.validated_data["old_password"]):
                logger.warning(f"Change password failed - wrong old password: {user.email}")
                return error_response("Old password is incorrect")

            user.set_password(serializer.validated_data["new_password"])
            user.save()

            try:
                send_reset_password_success_email(user)
            except Exception as e:
                logger.error(f"Change password email failed for {user.email}: {e}")

            logger.info(f"Password changed successfully: {user.email}")
            return success_response("Password changed successfully")

        logger.warning(f"Change password validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]

            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                logger.warning(f"Forgot password failed - user not found: {email}")
                return error_response("User with this email does not exist")

            otp_code = generate_otp()

            OTP.objects.create(
                user=user,
                otp=otp_code,
                otp_type="password_reset"
            )

            try:
                send_forgot_password_email(user, otp_code)
            except Exception as e:
                logger.error(f"Forgot password email failed for {user.email}: {e}")

            logger.info(f"Password reset OTP sent: {user.email}")
            return success_response("Password reset OTP sent successfully")

        logger.warning(f"Forgot password validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            otp_code = serializer.validated_data["otp"]
            new_password = serializer.validated_data["new_password"]

            try:
                user = CustomUser.objects.get(email=email)
                otp_obj = OTP.objects.filter(
                    user=user,
                    otp=otp_code,
                    otp_type="password_reset",
                    is_used=False
                ).latest("created_at")
            except Exception:
                logger.warning(f"Reset password failed - invalid OTP/email: {email}")
                return error_response("Invalid OTP or email")

            if not otp_obj.is_valid():
                logger.warning(f"Reset password OTP expired or used for: {email}")
                return error_response("OTP expired or already used")

            otp_obj.is_used = True
            otp_obj.save()

            user.set_password(new_password)
            user.save()

            try:
                send_reset_password_success_email(user)
            except Exception as e:
                logger.error(f"Reset password success email failed for {user.email}: {e}")

            logger.info(f"Password reset successfully: {user.email}")
            return success_response("Password reset successfully")

        logger.warning(f"Reset password validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = Address.objects.filter(user=request.user)
        serializer = AddressSerializer(addresses, many=True)
        return success_response("Addresses fetched successfully", serializer.data)

    def post(self, request):
        serializer = AddressSerializer(data=request.data)

        if serializer.is_valid():
            if serializer.validated_data.get("is_default"):
                Address.objects.filter(user=request.user).update(is_default=False)

            address = serializer.save(user=request.user)
            logger.info(f"Address added for user {request.user.email}: {address.id}")

            return success_response(
                "Address added successfully",
                serializer.data,
                status.HTTP_201_CREATED
            )

        logger.warning(f"Address add failed for {request.user.email}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            address = Address.objects.get(pk=pk, user=request.user)
        except Address.DoesNotExist:
            logger.warning(f"Address fetch failed for {request.user.email}: {pk}")
            return error_response("Address not found", status.HTTP_404_NOT_FOUND)

        serializer = AddressSerializer(address)
        return success_response("Address fetched successfully", serializer.data)

    def put(self, request, pk):
        try:
            address = Address.objects.get(pk=pk, user=request.user)
        except Address.DoesNotExist:
            logger.warning(f"Address update failed for {request.user.email}: {pk}")
            return error_response("Address not found", status.HTTP_404_NOT_FOUND)

        serializer = AddressSerializer(address, data=request.data, partial=True)

        if serializer.is_valid():
            if serializer.validated_data.get("is_default"):
                Address.objects.filter(user=request.user).update(is_default=False)

            serializer.save()
            logger.info(f"Address updated for user {request.user.email}: {pk}")
            return success_response("Address updated successfully", serializer.data)

        logger.warning(f"Address update validation failed for {request.user.email}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            address = Address.objects.get(pk=pk, user=request.user)
        except Address.DoesNotExist:
            logger.warning(f"Address delete failed for {request.user.email}: {pk}")
            return error_response("Address not found", status.HTTP_404_NOT_FOUND)

        address.delete()
        logger.info(f"Address deleted for user {request.user.email}: {pk}")
        return success_response("Address deleted successfully")


class SetDefaultAddressView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            address = Address.objects.get(
                pk=pk,
                user=request.user
            )
        except Address.DoesNotExist:
            logger.warning(f"Set default address failed for {request.user.email}: {pk}")
            return error_response(
                "Address not found",
                status.HTTP_404_NOT_FOUND
            )

        Address.objects.filter(
            user=request.user
        ).update(is_default=False)

        address.is_default = True
        address.save()

        serializer = AddressSerializer(address)

        logger.info(f"Default address updated for user {request.user.email}: {pk}")

        return success_response(
            "Default address updated successfully",
            serializer.data
        )