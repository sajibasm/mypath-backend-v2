from django.core.cache import cache
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import random


def generate_verification_code(length=6):
    return ''.join(random.choices('0123456789', k=length))

def store_verification_code(email, code, ttl=600):  # 10 minutes
    key = f"verify-code:{email}"
    cache.set(key, code, ttl)

def get_stored_verification_code(email):
    return cache.get(f"verify-code:{email}")

def delete_verification_code(email):
    cache.delete(f"verify-code:{email}")

def generate_email_verification_token(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token