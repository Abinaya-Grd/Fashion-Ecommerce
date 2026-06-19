from io import BytesIO

from django.http import FileResponse
from django.utils import timezone

from reportlab.pdfgen import canvas

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from .models import Invoice
from .serializers import InvoiceSerializer
from orders.models import Order


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


class MyInvoicesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        invoices = Invoice.objects.filter(
            order__user=request.user
        ).order_by('-invoiceid')

        serializer = InvoiceSerializer(invoices, many=True)

        return success_response(
            "Invoices fetched successfully",
            serializer.data
        )


class InvoiceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            invoice = Invoice.objects.get(
                invoiceid=pk,
                order__user=request.user
            )
        except Invoice.DoesNotExist:
            return error_response(
                "Invoice not found",
                status.HTTP_404_NOT_FOUND
            )

        serializer = InvoiceSerializer(invoice)

        return success_response(
            "Invoice fetched successfully",
            serializer.data
        )


    def delete(self, request, pk):
        try:
            invoice = Invoice.objects.get(invoiceid=pk)
        except invoice.DoesNotExist:
            return error_response("Invoice not found", status.HTTP_404_NOT_FOUND)

        invoice.delete()
        return success_response("Invoice deleted successfully")

class GenerateInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):

        try:
            order = Order.objects.get(
                orderid=order_id,
                user=request.user
            )
        except Order.DoesNotExist:
            return error_response(
                "Order not found",
                status.HTTP_404_NOT_FOUND
            )

        if order.payment_status != "paid":
            return error_response(
                "Invoice available only for paid orders"
            )

        invoice, created = Invoice.objects.get_or_create(
            order=order,
            defaults={
                "invoice_number": f"INV-{order.orderid}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            }
        )

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)

        y = 800

        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(100, y, "Fashion Ecommerce Invoice")

        y -= 40
        pdf.setFont("Helvetica", 11)
        pdf.drawString(100, y, f"Invoice No: {invoice.invoice_number}")

        y -= 25
        pdf.drawString(100, y, f"Order ID: {order.orderid}")

        y -= 25
        pdf.drawString(100, y, f"Invoice Date: {timezone.now().strftime('%d-%m-%Y %I:%M %p')}")

        y -= 25
        pdf.drawString(100, y, f"Customer: {request.user.username}")

        y -= 25
        pdf.drawString(100, y, f"Phone: {order.phone}")

        y -= 25
        pdf.drawString(100, y, f"Shipping Address: {order.shipping_address}")

        y -= 40
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, y, "Product")
        pdf.drawString(300, y, "Qty")
        pdf.drawString(360, y, "Price")
        pdf.drawString(450, y, "Total")

        y -= 20
        pdf.setFont("Helvetica", 11)

        for item in order.items.all():
            product_name = item.product.name[:25]

            pdf.drawString(100, y, product_name)
            pdf.drawString(300, y, str(item.quantity))
            pdf.drawString(360, y, f"Rs. {item.price}")
            pdf.drawString(450, y, f"Rs. {item.total_price}")

            y -= 20

            if y < 100:
                pdf.showPage()
                y = 800
                pdf.setFont("Helvetica", 11)

        y -= 30

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(350, y, f"Subtotal: Rs. {order.total_amount}")

        y -= 25
        pdf.drawString(350, y, f"Discount: Rs. {order.discount_amount}")

        y -= 25
        pdf.drawString(350, y, f"Final Amount: Rs. {order.final_amount}")

        y -= 25
        pdf.drawString(350, y, f"Payment Status: {order.payment_status}")

        y -= 25
        pdf.drawString(350, y, f"Order Status: {order.order_status}")

        y -= 50
        pdf.setFont("Helvetica", 10)
        pdf.drawString(100, y, "Thank you for shopping with us!")

        pdf.save()

        buffer.seek(0)

        return FileResponse(
            buffer,
            as_attachment=True,
            filename=f"{invoice.invoice_number}.pdf"
        )