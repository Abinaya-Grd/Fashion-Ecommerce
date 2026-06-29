from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Wallet, WalletTransaction
from .serializers import WalletSerializer, WalletTransactionSerializer
from notifications.models import Notification


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


class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet, created = Wallet.objects.get_or_create(
            user=request.user
        )

        serializer = WalletSerializer(wallet)

        return success_response(
            "Wallet fetched successfully",
            serializer.data
        )


class WalletHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet, created = Wallet.objects.get_or_create(
            user=request.user
        )

        transactions = wallet.transactions.all().order_by("-transactionid")

        serializer = WalletTransactionSerializer(
            transactions,
            many=True
        )

        return success_response(
            "Wallet history fetched successfully",
            serializer.data
        )


class AddMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")

        if not amount:
            return error_response("Amount is required")

        amount = Decimal(amount)

        if amount <= 0:
            return error_response("Invalid amount")

        wallet, created = Wallet.objects.get_or_create(
            user=request.user
        )

        wallet.balance += amount
        wallet.save()

        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type="credit",
            amount=amount,
            description="Money added to wallet"
        )

        Notification.objects.create(
            user=request.user,
            title="Wallet Credited",
            message=f"₹{amount} added to your wallet.",
            notification_type="wallet"
        )

        serializer = WalletSerializer(wallet)

        return success_response(
            "Money added successfully",
            serializer.data,
            status.HTTP_201_CREATED
        )


class WithdrawMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")

        if not amount:
            return error_response("Amount is required")

        amount = Decimal(amount)

        wallet, created = Wallet.objects.get_or_create(
            user=request.user
        )

        if wallet.balance < amount:
            return error_response("Insufficient wallet balance")

        wallet.balance -= amount
        wallet.save()

        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type="debit",
            amount=amount,
            description="Money withdrawn"
        )

        Notification.objects.create(
            user=request.user,
            title="Wallet Debited",
            message=f"₹{amount} withdrawn from your wallet.",
            notification_type="wallet"
        )

        serializer = WalletSerializer(wallet)

        return success_response(
            "Money withdrawn successfully",
            serializer.data
        )