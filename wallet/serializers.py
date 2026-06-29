from rest_framework import serializers
from .models import Wallet, WalletTransaction


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = [
            "transactionid",
            "transaction_type",
            "amount",
            "description",
            "created_at",
        ]


class WalletSerializer(serializers.ModelSerializer):
    transactions = WalletTransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Wallet
        fields = [
            "walletid",
            "user",
            "balance",
            "transactions",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "user",
            "balance",
            "created_at",
            "updated_at",
        ]