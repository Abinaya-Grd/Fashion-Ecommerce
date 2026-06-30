from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.permissions import IsAdminRole
from .models import Supplier
from .serializers import SupplierSerializer


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


class SupplierListCreateView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        suppliers = Supplier.objects.all().order_by("-supplierid")
        serializer = SupplierSerializer(suppliers, many=True)

        return success_response(
            "Suppliers fetched successfully",
            serializer.data
        )

    def post(self, request):
        serializer = SupplierSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return success_response(
                "Supplier created successfully",
                serializer.data,
                status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=400)


class SupplierDetailView(APIView):
    permission_classes = [IsAdminRole]

    def get_object(self, pk):
        try:
            return Supplier.objects.get(supplierid=pk)
        except Supplier.DoesNotExist:
            return None

    def get(self, request, pk):
        supplier = self.get_object(pk)

        if not supplier:
            return error_response(
                "Supplier not found",
                status.HTTP_404_NOT_FOUND
            )

        serializer = SupplierSerializer(supplier)

        return success_response(
            "Supplier fetched successfully",
            serializer.data
        )

    def put(self, request, pk):
        supplier = self.get_object(pk)

        if not supplier:
            return error_response(
                "Supplier not found",
                status.HTTP_404_NOT_FOUND
            )

        serializer = SupplierSerializer(
            supplier,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return success_response(
                "Supplier updated successfully",
                serializer.data
            )

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        supplier = self.get_object(pk)

        if not supplier:
            return error_response(
                "Supplier not found",
                status.HTTP_404_NOT_FOUND
            )

        supplier.delete()

        return success_response(
            "Supplier deleted successfully"
        )


class ActiveSupplierView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        suppliers = Supplier.objects.filter(
            status="active"
        )

        serializer = SupplierSerializer(
            suppliers,
            many=True
        )

        return success_response(
            "Active suppliers fetched successfully",
            serializer.data
        )