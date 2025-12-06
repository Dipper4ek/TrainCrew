import json
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from .models import Profile, Chat, Post, UserLocation
from django.shortcuts import render, get_object_or_404
from .forms import MessageForm
from django.http import JsonResponse
from django.core.mail import send_mail
from .forms import RegisterForm
from .models import EmailVerification
import random


def verify_email(request, user_id):
    user = User.objects.get(id=user_id)
    verification = EmailVerification.objects.get(user=user)

    if request.method == "POST":
        code = request.POST['code']
        if verification.code == code and not verification.is_expired():
            user.is_active = True
            user.save()
            verification.delete()  # видаляємо код після успішної активації
            login(request, user)
            return redirect("profile")
        else:
            return render(request, "app/verify_email.html", {"error": "Невірний або прострочений код"})

    return render(request, "app/verify_email.html")

@login_required
def map_view(request):
    return render(request, "app/map.html")


def get_all_locations(request):
    users = UserLocation.objects.select_related("user")

    data = []
    for u in users:
        data.append({
            "id": u.user.id,
            "username": u.user.username,
            "lat": u.latitude,
            "lng": u.longitude
        })

    return JsonResponse(data, safe=False)


@csrf_exempt
@login_required
def update_location(request):
    if request.method == "POST":
        data = json.loads(request.body)

        lat = data["lat"]
        lng = data["lng"]

        UserLocation.objects.update_or_create(
            user=request.user,
            defaults={"latitude": lat, "longitude": lng}
        )

        return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"})





class HomePageView(View):

    def get(self, request):
        return render(request, 'app/home_page.html')


def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            return render(request, "app/register.html", {"error": "User already exists"})

        # Створюємо користувача, але робимо його неактивним
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False
        user.save()

        # Створюємо код підтвердження
        code = str(random.randint(100000, 999999))
        EmailVerification.objects.create(user=user, code=code)

        # Відправляємо код на email
        send_mail(
            "Код підтвердження реєстрації",
            f"Ваш код: {code}",
            "noreply@traincrew.com",
            [email],
        )

        return redirect("verify_email", user_id=user.id)

    return render(request, "app/register.html")


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home_page')
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
    profile = get_object_or_404(Profile, user__username=username)
    is_owner = request.user.is_authenticated and request.user.username == username

    posts_count = Post.objects.filter(author=profile.user).count()
    followers_count = profile.followers.count()
    following_count = request.user.following.count() if request.user.is_authenticated else profile.user.following.count()

    return render(request, 'app/profile.html', {
        'profile': profile,
        'owner': is_owner,
        'posts_count': posts_count,
        'followers_count': followers_count,
        'following_count': following_count,
    })
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

    if query:
        # Пошук по username або по профілю name
        results = User.objects.filter(username__icontains=query).union(
            User.objects.filter(profile__name__icontains=query)
        )
    else:
        # Якщо пошук порожній, показуємо всіх користувачів
        results = User.objects.all()

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


@login_required
def follow_toggle(request, username):
    other_user = get_object_or_404(User, username=username)
    profile = other_user.profile

    if request.user in profile.followers.all():
        profile.followers.remove(request.user)  # відписка
    else:
        profile.followers.add(request.user)     # підписка

    return redirect('user_profile', username=username)