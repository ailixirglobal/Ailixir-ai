from django.http import JsonResponse
from .models import AuthToken


def get_token_from_request(request):
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Token "):
        return auth.split("Token ")[1].strip()
    return None


def authenticate_request(request):
    token_key = get_token_from_request(request)
    if not token_key:
        return None

    try:
        token = AuthToken.objects.get(key=token_key)
        return token.user
    except AuthToken.DoesNotExist:
        return None