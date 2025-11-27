import os
import requests
from .models import AISetting, RequestLog, PromptLog, AuthToken, QuickPrompt
from django.utils import timezone

from django.http import JsonResponse

API_URL = "https://router.huggingface.co/v1/chat/completions"


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

def check_rate_limit(request, limit=0):
    user = request.user if request.user.is_authenticated else None
    today = timezone.now().date()

    # Get or create today's log
    log, created = RequestLog.objects.get_or_create(user=user, date=today)

    # Check limit
    if log.count >= limit:
        return False  # limit reached

    # Still allowed → increase count
    log.count += 1
    log.save()
    return True

def make_query(request, prompt, is_public=False, old_messages=[], quick_prompt_id=None):
    # Load system settings
    settings_obj = AISetting.objects.first()

    # Safety fallback if settings not created
    if not settings_obj:
        return {"error": "System settings not configured."}
    
    # to check if user can make request
    if (not request.username == 'public' ) and ( not check_rate_limit(request, settings_obj.limit_per_day) ):
      return {"error": "You have Exhusted your daily request.\nTry again tomorrow."}
      
    
    # Example logic using your settings
    data = {
        "model": settings_obj.model_name,
        "token": settings_obj.huggingface_token,
        "limit": settings_obj.limit_per_day,
        "system_prompt": settings_obj.system_prompt,
        "research_enabled": settings_obj.research_exp,
        "user": request.user.username if request.user.is_authenticated else "guest",
        "query": prompt,
        }
    
    
    # create promt log after ai response
    system_prompt = {
      'role': 'system',
      'content': data.get('system_prompt', '')
    }
    user_prompt = {
      "role": "user",
      "content": prompt
      }
    if quick_prompt_id:
      quick_prompt = QuickPrompt.objects.get(id=int(quick_prompt_id))
      old_messages += [{'role':'assistant','content':quick_prompt.prompt}]
    messages = [system_prompt] + old_messages + [user_prompt]
    response = query(data, {
        "messages": messages,
        "model": settings_obj.model_name
    })
    PromptLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        prompt=prompt,
        response=response,
        model_used=settings_obj.model_name
    )
    data['response'] = response

    return data
    
    



def query(data, payload):
    headers = {
      "Authorization": f"Bearer {data.get('token')}",
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

