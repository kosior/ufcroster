from django.core import signing


def generate_token(email, is_active):
    return signing.dumps((email, is_active))
