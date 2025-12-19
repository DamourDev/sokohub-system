from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from allauth.account.signals import user_signed_up
from .models import CustomUser

@receiver(user_signed_up)
def send_welcome_email(request, user, **kwargs):
    """
    This function runs automatically ONLY when a user successfully signs up.
    """
    # This check ensures we only send it if they have an email address
    if user.email:
        subject = 'Welcome to SokoHub!'
        
        # Your exact message logic:
        message = f"Hi {user.username},\n\nCongratulations! You are now a registered member of SokoHub.\n\nYou can now browse sell, buy products on your convenience.\n\nThank you for joining us!"
        
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]

        try:
            send_mail(subject, message, from_email, recipient_list)
            # You can remove this print statement later if you want
            print(f"Welcome email sent to {user.email}")
        except Exception as e:
            print(f"Error sending email: {e}")