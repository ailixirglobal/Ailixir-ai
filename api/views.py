from django.shortcuts import render
from django.http import JsonResponse
from core.utils import make_query
from django.views.decorators.csrf import csrf_exempt
from core.decorators import token_required
# Create your views here.

@csrf_exempt
@token_required
def v1_api_endpoint(request):
  
  if request.method == 'POST':
    prompt = request.POST.get('prompt')
    response = make_query(request, prompt)
    choices = response['response']['choices']
    message = choices[0]['message']
    return JsonResponse(message)
  return JsonResponse({"error": "Invalid Request Method"})