from functools import wraps
from django.http import JsonResponse
from .auth_utils import authenticate_request


def token_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        user = authenticate_request(request)
        if not user:
            return JsonResponse({"error": "Invalid or missing token"}, status=401)
        request.username = user
        
        return view_func(request, *args, **kwargs)
    return _wrapped