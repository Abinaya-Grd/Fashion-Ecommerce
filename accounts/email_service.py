from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


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


def send_verification_email(user, otp):
    send_html_email(
        subject="Verify Your Email - SSS Fashions",
        template_name="emails/verify_email.html",
        context={
            "username": user.username,
            "otp": otp,
        },
        to_email=user.email,
    )


def send_forgot_password_email(user, otp):
    send_html_email(
        subject="Password Reset OTP - SSS Fashions",
        template_name="emails/forgot_password.html",
        context={
            "username": user.username,
            "otp": otp,
        },
        to_email=user.email,
    )


def send_reset_password_success_email(user):
    send_html_email(
        subject="Password Reset Successful - SSS Fashions",
        template_name="emails/reset_password.html",
        context={
            "username": user.username,
        },
        to_email=user.email,
    )


def send_welcome_email(user):
    send_html_email(
        subject="Welcome to SSS Fashions",
        template_name="emails/welcome.html",
        context={
            "username": user.username,
        },
        to_email=user.email,
    )