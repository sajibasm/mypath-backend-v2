# account/tasks.py
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings
from email.utils import formataddr

@shared_task
def send_welcome_email(name, email):
    subject = "Welcome to MyPath!"
    from_email = f"MyPath <{settings.EMAIL_HOST_USER}>"
    to = [email]

    template = get_template("email/welcome_email.html")
    html_content = template.render({"name": name})

    msg = EmailMultiAlternatives(subject, "", from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

@shared_task
def send_email_verification_link(name, email, uid, token):
    verification_link = f"{settings.FRONTEND_URL}//api/user/verify-email/{uid}/{token}/"
    template = get_template("email/verify_email_link.html")
    html_content = template.render({
        "name": name,
        "verification_link": verification_link,
    })

    subject = "Verify Your Email - MyPath"
    from_email = f"MyPath <{settings.EMAIL_HOST_USER}>"
    msg = EmailMultiAlternatives(subject, "", from_email, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()



@shared_task
def send_password_reset_otp_email(name, email, code):
    subject = "Your OTP for Password Reset"
    from_email = f"MyPath <{settings.EMAIL_HOST_USER}>"
    to = [email]

    template = get_template("email/password_reset_code.html")
    html_content = template.render({
        "name": name,
        "email": email,
        "code": code,
    })

    msg = EmailMultiAlternatives(subject, "", from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

@shared_task
def password_reset_successful(name, email,):
    subject = "Your Password Has Been Changed"
    from_email = f"MyPath <{settings.EMAIL_HOST_USER}>"
    to = [email]
    template = get_template("email/password_reset_success.html")
    html_content = template.render({"name": name})

    msg = EmailMultiAlternatives(subject, "", from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()