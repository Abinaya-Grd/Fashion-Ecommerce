from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_html_email(subject, template_name, context, to_email):
    html_content = render_to_string(template_name, context)

    email = EmailMultiAlternatives(
        subject=subject,
        body="",
        from_email=f"SSS Fashions <{settings.EMAIL_HOST_USER}>",
        to=[to_email],
    )

    email.attach_alternative(html_content, "text/html")
    email.send()


def send_order_status_email(order):
    send_html_email(
        subject=f"Order #{order.orderid} Status Update - SSS Fashions",
        template_name="emails/order_status.html",
        context={
            "username": order.user.username,
            "orderid": order.orderid,
            "order_status": order.order_status,
            "payment_status": order.payment_status,
            "final_amount": order.final_amount,
        },
        to_email=order.user.email,
    )

    print("Order status email sent successfully")