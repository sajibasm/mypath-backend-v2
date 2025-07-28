# utils/reset_code.py
from django.core import signing
import random
from django.core.cache import cache

def generate_code():
    return ''.join(random.choices('0123456789', k=6))

def store_code(email, code, ttl=6000):
    signed_code = signing.dumps(code)
    cache.set(f"reset_code:{email}", signed_code, timeout=ttl)

def get_stored_code(email):
    signed_code = cache.get(f"reset_code:{email}")
    if signed_code:
        try:
            return signing.loads(signed_code)
        except signing.BadSignature:
            return None
    return None

def delete_code(email):
    cache.delete(f"reset_code:{email}")

def can_send_new_code(email, cooldown=60):
    """Returns True if new code can be sent (not within cooldown)"""
    key = f"reset_code:cooldown:{email}"
    if cache.get(key):
        return False
    cache.set(key, True, timeout=cooldown)
    return True