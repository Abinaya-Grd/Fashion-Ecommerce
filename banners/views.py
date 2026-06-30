from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Banner
from .serializers import BannerSerializer
from accounts.permissions import IsAdminRole


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


class BannerListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminRole()]
        return []

    def get(self, request):
        banners = Banner.objects.all()

        serializer = BannerSerializer(
            banners,
            many=True,
            context={"request": request}
        )

        return success_response(
            "Banners fetched successfully",
            serializer.data
        )

    def post(self, request):

        serializer = BannerSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return success_response(
                "Banner created successfully",
                serializer.data,
                status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=400)


class BannerDetailView(APIView):

    def get_permissions(self):
        if self.request.method in ["PUT", "DELETE"]:
            return [IsAdminRole()]
        return []

    def get_object(self, pk):
        try:
            return Banner.objects.get(bannerid=pk)
        except Banner.DoesNotExist:
            return None

    def get(self, request, pk):

        banner = self.get_object(pk)

        if not banner:
            return error_response("Banner not found", 404)

        serializer = BannerSerializer(
            banner,
            context={"request": request}
        )

        return success_response(
            "Banner fetched successfully",
            serializer.data
        )

    def put(self, request, pk):

        banner = self.get_object(pk)

        if not banner:
            return error_response("Banner not found", 404)

        serializer = BannerSerializer(
            banner,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return success_response(
                "Banner updated successfully",
                serializer.data
            )

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):

        banner = self.get_object(pk)

        if not banner:
            return error_response("Banner not found", 404)

        banner.delete()

        return success_response(
            "Banner deleted successfully"
        )


class ActiveBannerView(APIView):

    def get(self, request):

        today = timezone.now().date()

        banners = Banner.objects.filter(
            status="active",
            start_date__lte=today,
            end_date__gte=today
        )

        serializer = BannerSerializer(
            banners,
            many=True,
            context={"request": request}
        )

        return success_response(
            "Active banners fetched successfully",
            serializer.data
        )


class WebBannerView(APIView):

    def get(self, request):

        banners = Banner.objects.filter(
            device__in=["web", "both"],
            status="active"
        )

        serializer = BannerSerializer(
            banners,
            many=True,
            context={"request": request}
        )

        return success_response(
            "Web banners fetched successfully",
            serializer.data
        )


class MobileBannerView(APIView):

    def get(self, request):

        banners = Banner.objects.filter(
            device__in=["mobile", "both"],
            status="active"
        )

        serializer = BannerSerializer(
            banners,
            many=True,
            context={"request": request}
        )

        return success_response(
            "Mobile banners fetched successfully",
            serializer.data
        )