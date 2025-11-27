from django.shortcuts import render
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile, Chat
from django.shortcuts import render, get_object_or_404
from .forms import MessageForm
from django.http import JsonResponse

class HomePageView(View):

    def get(self, request):
        return render(request, 'app/home_page.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']  # для входу
        password = request.POST['password']
        display_name = request.POST['display_name']  # нове поле для публічного імені

        if User.objects.filter(username=username).exists():
            messages.error(request, "User already exists!")
            return redirect('register')

        # Створюємо користувача
        user = User.objects.create_user(username=username, password=password)
        login(request, user)

        # Створюємо профіль з display_name
        Profile.objects.create(user=user, name=display_name)

        return redirect('profile')

    return render(request, 'app/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        messages.error(request, "Невірний логін або пароль!")
        return redirect('login')
    return render(request, 'app/login.html')

def logout_view(request):
    logout(request)
    return redirect('home_page')

@login_required
def profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'app/profile.html', {'profile': profile, 'owner': True})

def user_profile(request, username):
    # отримуємо профіль за username користувача
    profile = get_object_or_404(Profile, user__username=username)
    # перевіряємо, чи це твій профіль
    is_owner = request.user.is_authenticated and request.user.username == username
    return render(request, 'app/profile.html', {'profile': profile, 'owner': is_owner})
@login_required
def edit_profile(request):
    profile = request.user.profile  # отримуємо профіль поточного користувача

    if request.method == 'POST':
        profile = request.user.profile
        avatar = request.FILES.get('avatar')
        if avatar:
            profile.avatar = avatar
        profile.name = request.POST.get('name', profile.name)
        profile.bio = request.POST.get('bio', profile.bio)
        profile.save()

        return redirect('profile')

    return render(request, 'app/edit_profile.html', {'profile': profile})

def user_search(request):
    query = request.GET.get('q', '')  # отримуємо параметр ?q=...
    results = []

    if query:
        # Пошук по username або по профілю name
        results = User.objects.filter(
            username__icontains=query
        ).union(
            User.objects.filter(profile__name__icontains=query)
        )

    return render(request, 'app/user_search.html', {'results': results, 'query': query})


@login_required
def chat_list(request):
    # Список чатів поточного користувача
    chats = request.user.chats.all().order_by('-created_at')
    return render(request, 'app/chat_list.html', {'chats': chats})

@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in chat.participants.all():
        return redirect('chat_list')  # Якщо користувач не учасник чату

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat = chat
            message.sender = request.user
            message.save()
            return redirect('chat_detail', chat_id=chat.id)
    else:
        form = MessageForm()

    messages = chat.messages.order_by('timestamp')
    return render(request, 'app/chat_detail.html', {'chat': chat, 'messages': messages, 'form': form})

@login_required
def start_chat(request, username):
    other_user = get_object_or_404(User, username=username)
    # Шукаємо чат між двома користувачами
    chat = Chat.objects.filter(participants=request.user).filter(participants=other_user).first()
    if not chat:
        chat = Chat.objects.create()
        chat.participants.add(request.user, other_user)
        chat.save()
    return redirect('chat_detail', chat_id=chat.id)


@login_required
def chat_messages_json(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in chat.participants.all():
        return JsonResponse({'error': 'Forbidden'}, status=403)

    messages = chat.messages.order_by('timestamp')
    data = [{
        'sender': msg.sender.username,
        'content': msg.content,
        'timestamp': msg.timestamp.strftime("%H:%M:%S")
    } for msg in messages]
    return JsonResponse({'messages': data})