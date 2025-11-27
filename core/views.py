from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import AISetting, QuickPrompt
from .forms import AISettingForm
from .utils import make_query

def public_ai_interface(request):
  context = {'quick_prompts': QuickPrompt.objects.all()}
  username = request.session.get('username')
  messages = request.session.get('messages', [])
  request.username = 'public'
  if username:
    context['usersession'] = username
  if request.method == 'POST':
    if request.htmx:
      userinput = request.POST.get('userinput')
      qp_id = request.GET.get('qp', None)
      
      response = make_query(request, userinput, is_public=True, old_messages=messages, quick_prompt_id=qp_id)
      content = 'Error Occured'
      if 'choices' in response['response']:
        choice = response['response']['choices'][0]
        content = choice['message']['content']
      ai_message = {
        'role': 'assistant',
        'content': content
      }
      user_message = {
        'role': 'user',
        'content': userinput
      }
      messages.append(user_message)
      messages.append(ai_message)
      request.session['messages'] = messages
      return render(request, 'core/_message.html', {'message': ai_message})
    username = request.POST.get('username', '')
    if username == '':
      return redirect('public_ai_interface')
    
    userinput = 'Hello!, my name is ' + username
    initial_prompt = {
        'role' : 'user',
        'content' : userinput
    }
    #messages.append(initial_prompt)
    response = make_query(request, userinput, is_public=True)
    content = 'Error Occured'
    if 'choices' in response['response']:
        choice = response['response']['choices'][0]
        message = choice['message']
        messages.append(message)
      
    request.session['messages'] = messages
    request.session['username'] = username
    request.session.set_expiry(0)
    return redirect('public_ai_interface')
  # if request.htmx:
  #   return render(request, 'core/_messages.html', {'messages': messages})
  return render(request, 'core/chat.html', context)

def quick_prompt_interface(request, id=None):
  context = {}
  quick_prompt = QuickPrompt.objects.get(id=id)
  messages = []
  context['messages'] = messages
  context['qp'] = quick_prompt
  messages.append({'role':'assistant','content':quick_prompt.prompt})
  return render(request, 'core/chat.html', context)
  

def edit_settings(request):
    # Get the first (and only) settings instance, or create one
    settings_obj, created = AISetting.objects.get_or_create(id=1)

    if request.method == "POST":
        form = AISettingForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            return redirect('edit_settings')  # or any success page

    else:
        form = AISettingForm(instance=settings_obj)

    return render(request, 'admin/settings_page.html', {'form': form})